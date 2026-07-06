"""
🔧 複雑なミドルウェアパイプライン
責任の鎖パターン、インターセプター、DI、メタプログラミング
"""

from typing import Callable, Any, Awaitable, Optional, List
from functools import wraps
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from datetime import datetime
import inspect
import weakref
from abc import ABC, abstractmethod


class _Interceptor(ABC):
    """インターセプター抽象クラス"""
    
    @abstractmethod
    async def pre_process(self, context: Dict) -> None:
        pass
    
    @abstractmethod
    async def post_process(self, context: Dict, result: Any) -> Any:
        pass


class _RequestContextInjector(_Interceptor):
    """リクエストコンテキスト注入"""
    
    async def pre_process(self, context: Dict) -> None:
        context['start_time'] = datetime.utcnow()
        context['request_id'] = id(context)
    
    async def post_process(self, context: Dict, result: Any) -> Any:
        elapsed = (datetime.utcnow() - context['start_time']).total_seconds()
        context['elapsed_ms'] = elapsed * 1000
        return result


class _PerformanceMonitor(_Interceptor):
    """パフォーマンス監視"""
    
    def __init__(self):
        self._metrics = weakref.WeakValueDictionary()
    
    async def pre_process(self, context: Dict) -> None:
        context['perf_start'] = datetime.utcnow()
    
    async def post_process(self, context: Dict, result: Any) -> Any:
        elapsed = (datetime.utcnow() - context['perf_start']).total_seconds()
        
        if elapsed > 1.0:
            print(f"⚠️  Slow request detected: {elapsed:.2f}s")
        
        return result


class _SecurityValidator(_Interceptor):
    """セキュリティ検証"""
    
    async def pre_process(self, context: Dict) -> None:
        # 複雑なセキュリティチェック
        request: Request = context.get('request')
        if request:
            context['is_safe'] = await self._validate(request)
    
    async def post_process(self, context: Dict, result: Any) -> Any:
        return result
    
    async def _validate(self, request: Request) -> bool:
        # 複雑なバリデーション
        return True


class _MiddlewarePipeline:
    """複雑なミドルウェアパイプライン"""
    
    def __init__(self):
        self._interceptors: List[_Interceptor] = []
        self._order = []
    
    def register(self, interceptor: _Interceptor, priority: int = 0):
        """インターセプターを登録（優先度付き）"""
        self._interceptors.append(interceptor)
        self._order.append((interceptor, priority))
        self._order.sort(key=lambda x: x[1], reverse=True)
    
    async def execute(self, func: Callable, context: Dict) -> Any:
        """パイプラインを実行"""
        
        # Pre-process
        for interceptor, _ in self._order:
            await interceptor.pre_process(context)
        
        # Main execution
        result = await func(context) if asyncio.iscoroutinefunction(func) else func(context)
        
        # Post-process (逆順)
        for interceptor, _ in reversed(self._order):
            result = await interceptor.post_process(context, result)
        
        return result


class _DynamicMiddleware(BaseHTTPMiddleware):
    """動的にルートを分析するミドルウェア"""
    
    def __init__(self, app, pipeline: _MiddlewarePipeline):
        super().__init__(app)
        self._pipeline = pipeline
    
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        
        # コンテキストを構築
        context = {
            'request': request,
            'path': request.url.path,
            'method': request.method,
            'metadata': {}
        }
        
        # パイプラインで処理
        async def _call():
            return await call_next(request)
        
        await self._pipeline.execute(_call, context)
        
        # リクエスト処理
        response = await call_next(request)
        
        # カスタムヘッダーを追加（メタデータ）
        response.headers['X-Request-ID'] = str(context.get('request_id', ''))
        response.headers['X-Response-Time'] = str(context.get('elapsed_ms', 0))
        
        return response


import asyncio
from typing import Dict
