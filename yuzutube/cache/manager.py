"""
⚡ マルチレイヤーキャッシュマネージャー
適応型キャッシング、LRU削除、自動圧縮、メモリ最適化
"""

import asyncio
import hashlib
import pickle
import json
from typing import Any, Optional, Callable, Coroutine, Dict
from datetime import datetime, timedelta
from collections import OrderedDict
from abc import ABC, abstractmethod
import weakref
from functools import wraps
import zlib


class _CacheLayer(ABC):
    """キャッシュレイヤーの抽象基底クラス"""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int) -> None:
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> None:
        pass


class _L1MemoryCache(_CacheLayer):
    """第1層: 圧縮メモリキャッシュ（LRU）"""
    
    def __init__(self, max_size: int = 1000):
        self._cache: OrderedDict[str, tuple] = OrderedDict()
        self._max_size = max_size
        self._lock = asyncio.Lock()
        self._hit_count = 0
        self._miss_count = 0
    
    async def get(self, key: str) -> Optional[Any]:
        async with self._lock:
            if key in self._cache:
                value, expiry, compressed = self._cache.pop(key)
                
                if datetime.utcnow() > expiry:
                    self._miss_count += 1
                    return None
                
                self._cache[key] = (value, expiry, compressed)
                self._cache.move_to_end(key)
                self._hit_count += 1
                
                return zlib.decompress(value) if compressed else value
            
            self._miss_count += 1
            return None
    
    async def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        async with self._lock:
            # 値を圧縮
            serialized = pickle.dumps(value)
            compressed = zlib.compress(serialized)
            is_compressed = len(compressed) < len(serialized)
            
            final_value = compressed if is_compressed else serialized
            
            self._cache[key] = (
                final_value,
                datetime.utcnow() + timedelta(seconds=ttl),
                is_compressed
            )
            self._cache.move_to_end(key)
            
            # LRU削除
            while len(self._cache) > self._max_size:
                self._cache.popitem(last=False)
    
    async def delete(self, key: str) -> None:
        async with self._lock:
            self._cache.pop(key, None)
    
    def stats(self) -> dict:
        total = self._hit_count + self._miss_count
        return {
            'hit_rate': self._hit_count / total if total > 0 else 0,
            'entries': len(self._cache),
            'hits': self._hit_count,
            'misses': self._miss_count
        }


class _L2HashCache(_CacheLayer):
    """第2層: ハッシュベースのセカンダリキャッシュ"""
    
    def __init__(self):
        self._cache: Dict[str, tuple] = {}
        self._hash_index: Dict[str, list] = {}
        self._lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[Any]:
        async with self._lock:
            if key in self._cache:
                value, expiry = self._cache[key]
                
                if datetime.utcnow() > expiry:
                    del self._cache[key]
                    return None
                
                return value
            
            return None
    
    async def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        async with self._lock:
            self._cache[key] = (
                value,
                datetime.utcnow() + timedelta(seconds=ttl)
            )
            
            # ハッシュインデックスを更新
            h = hashlib.sha256(key.encode()).hexdigest()[:8]
            if h not in self._hash_index:
                self._hash_index[h] = []
            if key not in self._hash_index[h]:
                self._hash_index[h].append(key)
    
    async def delete(self, key: str) -> None:
        async with self._lock:
            self._cache.pop(key, None)


class _AdaptiveCacheManager:
    """適応型キャッシュマネージャー"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._l1 = _L1MemoryCache()
            cls._instance._l2 = _L2HashCache()
            cls._instance._config = {
                'enable_l1': True,
                'enable_l2': True,
                'compress_threshold': 1024,
                'auto_expire': True
            }
        return cls._instance
    
    async def get(self, key: str) -> Optional[Any]:
        """マルチレイヤーキャッシュ取得"""
        
        # L1を試す
        if self._config['enable_l1']:
            value = await self._l1.get(key)
            if value is not None:
                return value
        
        # L2を試す
        if self._config['enable_l2']:
            value = await self._l2.get(key)
            if value is not None:
                # L1に昇格
                if self._config['enable_l1']:
                    await self._l1.set(key, value, 3600)
                return value
        
        return None
    
    async def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """マルチレイヤーキャッシュ保存"""
        if self._config['enable_l1']:
            await self._l1.set(key, value, ttl)
        if self._config['enable_l2']:
            await self._l2.set(key, value, ttl)
    
    async def delete(self, key: str) -> None:
        """キャッシュ削除"""
        if self._config['enable_l1']:
            await self._l1.delete(key)
        if self._config['enable_l2']:
            await self._l2.delete(key)
    
    def cached(self, ttl: int = 3600):
        """複雑なキャッシュデコレータ"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # キャッシュキーを複雑に生成
                cache_key = hashlib.sha256(
                    json.dumps({
                        'func': func.__name__,
                        'args': str(args),
                        'kwargs': str(kwargs)
                    }, sort_keys=True, default=str).encode()
                ).hexdigest()
                
                # キャッシュから取得
                cached = await self.get(cache_key)
                if cached is not None:
                    return cached
                
                # 実行
                result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
                
                # キャッシュに保存
                await self.set(cache_key, result, ttl)
                
                return result
            
            return wrapper
        
        return decorator
    
    def stats(self) -> dict:
        """キャッシュ統計"""
        return {
            'l1': self._l1.stats(),
            'config': self._config
        }


# グローバルキャッシュマネージャー
cache_manager = _AdaptiveCacheManager()
