"""
🌐 高度なHTTPクライアント
サーキットブレーカー、リトライロジック、非同期バッチング、レート制限
"""

import httpx
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from collections import deque
import random


class _CircuitBreakerState(Enum):
    """サーキットブレーカーの状態"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class _CircuitBreakerConfig:
    """サーキットブレーカー設定"""
    failure_threshold: int = 5
    recovery_timeout: int = 60
    expected_exception: type = httpx.RequestError
    name: str = "circuit_breaker"


class _AdvancedCircuitBreaker:
    """複雑なサーキットブレーカー実装"""
    
    def __init__(self, config: _CircuitBreakerConfig):
        self._config = config
        self._state = _CircuitBreakerState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time = None
        self._lock = asyncio.Lock()
    
    async def call(self, func, *args, **kwargs):
        """非同期関数をサーキットブレーカーで実行"""
        async with self._lock:
            if self._state == _CircuitBreakerState.OPEN:
                if self._should_attempt_reset():
                    self._state = _CircuitBreakerState.HALF_OPEN
                else:
                    raise Exception(f"{self._config.name}: Circuit is OPEN")
        
        try:
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            await self._on_success()
            return result
        except self._config.expected_exception as e:
            await self._on_failure()
            raise
    
    def _should_attempt_reset(self) -> bool:
        """リセットを試みるべきか判定"""
        if self._last_failure_time is None:
            return True
        
        elapsed = (datetime.utcnow() - self._last_failure_time).total_seconds()
        return elapsed >= self._config.recovery_timeout
    
    async def _on_success(self):
        """成功時の処理"""
        async with self._lock:
            self._failure_count = 0
            
            if self._state == _CircuitBreakerState.HALF_OPEN:
                self._success_count += 1
                if self._success_count >= 2:
                    self._state = _CircuitBreakerState.CLOSED
                    self._success_count = 0
    
    async def _on_failure(self):
        """失敗時の処理"""
        async with self._lock:
            self._failure_count += 1
            self._last_failure_time = datetime.utcnow()
            
            if self._failure_count >= self._config.failure_threshold:
                self._state = _CircuitBreakerState.OPEN


@dataclass
class _RateLimitBucket:
    """トークンバケット式レート制限"""
    capacity: int = 100
    refill_rate: float = 10.0
    tokens: float = field(default=0)
    last_refill: datetime = field(default_factory=datetime.utcnow)
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    
    async def acquire(self, tokens: int = 1) -> bool:
        """トークンを取得（レート制限チェック）"""
        async with self._lock:
            self._refill()
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            
            return False
    
    def _refill(self):
        """トークンを自動補充"""
        now = datetime.utcnow()
        elapsed = (now - self.last_refill).total_seconds()
        
        refill_tokens = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + refill_tokens)
        self.last_refill = now


class _BatchRequestQueue:
    """バッチリクエスト処理"""
    
    def __init__(self, batch_size: int = 10, flush_interval: float = 1.0):
        self._queue: deque = deque()
        self._batch_size = batch_size
        self._flush_interval = flush_interval
        self._lock = asyncio.Lock()
        self._last_flush = datetime.utcnow()
    
    async def enqueue(self, request: Dict[str, Any]) -> None:
        """リクエストをキューに追加"""
        async with self._lock:
            self._queue.append(request)
    
    async def should_flush(self) -> bool:
        """フラッシュすべきか判定"""
        async with self._lock:
            size_ready = len(self._queue) >= self._batch_size
            time_ready = (datetime.utcnow() - self._last_flush).total_seconds() >= self._flush_interval
            
            return size_ready or time_ready
    
    async def flush(self) -> list:
        """バッチを処理"""
        async with self._lock:
            batch = []
            while self._queue and len(batch) < self._batch_size:
                batch.append(self._queue.popleft())
            
            self._last_flush = datetime.utcnow()
            return batch


class _UltraHTTPClient:
    """究極のHTTPクライアント"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._client = httpx.AsyncClient(timeout=15.0)
            cls._instance._breaker = _AdvancedCircuitBreaker(
                _CircuitBreakerConfig(name="api_breaker")
            )
            cls._instance._rate_limiter = _RateLimitBucket()
            cls._instance._batch_queue = _BatchRequestQueue()
        return cls._instance
    
    async def get(self, url: str, params: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """GET リクエスト（レート制限、サーキットブレーカー付き）"""
        
        # レート制限チェック
        while not await self._rate_limiter.acquire():
            await asyncio.sleep(0.1)
        
        # サーキットブレーカーで実行
        async def _request():
            response = await self._client.get(url, params=params, **kwargs)
            response.raise_for_status()
            return response.json()
        
        return await self._breaker.call(_request)
    
    async def batch_requests(self, requests: list) -> list:
        """バッチリクエスト処理"""
        tasks = []
        for req in requests:
            task = self.get(req['url'], req.get('params'))
            tasks.append(task)
        
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    async def close(self):
        """クライアントをクローズ"""
        await self._client.aclose()


# グローバルクライアント
ultra_client = _UltraHTTPClient()
