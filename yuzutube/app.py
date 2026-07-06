"""
⚡ 究極のFastAPIアプリケーション
複雑な初期化、非同期処理、メタプログラミング統合
"""

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional
import asyncio
from datetime import datetime
import json
import os

from yuzutube.security.crypto import _crypto_engine, _obfuscated_decorator
from yuzutube.cache.manager import cache_manager
from yuzutube.core.client import ultra_client
from yuzutube.middleware.pipeline import (
    _MiddlewarePipeline,
    _DynamicMiddleware,
    _RequestContextInjector,
    _PerformanceMonitor,
    _SecurityValidator
)
from yuzutube.core.router import _router, _HTTPMethod


class _AppConfig:
    """複雑なアプリケーション設定"""
    
    def __init__(self):
        self._config = {
            'api_url': 'https://helena-stating-families-plays.trycloudflare.com',
            'timeout': 15,
            'max_retries': 3,
            'cache_enabled': True,
            'security_enabled': True,
            'monitoring_enabled': True,
            'version': '2.0.0-ULTRA',
            'codename': 'PHANTOM_PROTOCOL'
        }
        self._initialized = False
    
    async def initialize(self):
        """複雑な初期化処理"""
        if self._initialized:
            return
        
        # マルチレイヤー初期化
        await self._init_crypto()
        await self._init_cache()
        await self._init_client()
        
        self._initialized = True
    
    async def _init_crypto(self):
        """暗号化システムの初期化"""
        # シグネチャとトークン生成
        token = _crypto_engine.tokens.issue(
            'yuzutube_service',
            {'tier': 'ultra', 'permissions': ['read', 'write']},
            ttl=86400
        )
        self._config['service_token'] = token
    
    async def _init_cache(self):
        """キャッシュシステムの初期化"""
        stats = cache_manager.stats()
        print(f"✅ Cache initialized: {stats}")
    
    async def _init_client(self):
        """HTTPクライアントの初期化"""
        print(f"✅ Ultra HTTP Client initialized")
    
    async def shutdown(self):
        """複雑なシャットダウン処理"""
        await ultra_client.close()
    
    def get(self, key: str, default=None):
        return self._config.get(key, default)


# グローバル設定
_config = _AppConfig()


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncGenerator:
    """複雑なアプリケーションライフサイクル"""
    
    # 起動時
    print("🚀 Initializing PHANTOM_PROTOCOL...")
    await _config.initialize()
    
    # ミドルウェアパイプラインを構築
    pipeline = _MiddlewarePipeline()
    pipeline.register(_RequestContextInjector(), priority=100)
    pipeline.register(_PerformanceMonitor(), priority=90)
    pipeline.register(_SecurityValidator(), priority=80)
    
    app.add_middleware(_DynamicMiddleware, pipeline=pipeline)
    
    print("✅ PHANTOM_PROTOCOL initialized successfully")
    
    yield
    
    # シャットダウン時
    print("🛑 Shutting down PHANTOM_PROTOCOL...")
    await _config.shutdown()
    print("✅ Shutdown complete")


class _UltraApp:
    """究極のアプリケーションクラス"""
    
    _instance: Optional['_UltraApp'] = None
    
    def __new__(cls) -> '_UltraApp':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """複雑な初期化"""
        self.app = FastAPI(
            title="yuzutube",
            version="2.0.0-ULTRA",
            description="Phantom Protocol Media Platform",
            lifespan=_lifespan
        )
        
        # CORS設定
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # ルートを動的に登録
        self._register_routes()
        
        # イベントハンドラー
        self._register_events()
    
    def _register_routes(self):
        """複雑なルート登録"""
        
        @_obfuscated_decorator
        async def search_handler(query: str, limit: int = 12):
            """検索エンドポイント"""
            return await self._search(query, limit)
        
        @_obfuscated_decorator
        async def home_handler():
            """ホームエンドポイント"""
            return await self._get_home()
        
        # ルートを登録
        self.app.get("/api/search")(lambda q: search_handler(q))
        self.app.get("/api/home")(home_handler)
        self.app.get("/", response_class=HTMLResponse)(self._index)
        self.app.get("/api/health")(self._health)
    
    def _register_events(self):
        """複雑なイベント登録"""
        
        @self.app.on_event("startup")
        async def startup():
            print("🔥 Application startup initiated")
        
        @self.app.on_event("shutdown")
        async def shutdown():
            print("❄️  Application shutdown initiated")
    
    @cache_manager.cached(ttl=300)
    async def _search(self, query: str, limit: int = 12) -> dict:
        """複雑な検索ロジック"""
        try:
            # 外部APIを呼び出し
            from yuzutube.core.client import ultra_client
            
            data = await ultra_client.get(
                f"{_config.get('api_url')}/search/{query}",
                params={"limit": min(limit, 100)}
            )
            
            # 結果を署名付きで返す
            signature = _crypto_engine.signature.sign(data)
            
            return {
                'data': data,
                'signature': signature,
                'timestamp': datetime.utcnow().isoformat(),
                'cached': False
            }
        except Exception as e:
            return {
                'error': str(e),
                'data': None,
                'timestamp': datetime.utcnow().isoformat()
            }
    
    @cache_manager.cached(ttl=600)
    async def _get_home(self) -> dict:
        """複雑なホーム取得"""
        try:
            from yuzutube.core.client import ultra_client
            
            data = await ultra_client.get(
                f"{_config.get('api_url')}/search/popular",
                params={"limit": 12}
            )
            
            signature = _crypto_engine.signature.sign(data)
            
            return {
                'data': data,
                'signature': signature,
                'timestamp': datetime.utcnow().isoformat(),
                'cached': False
            }
        except Exception as e:
            return {
                'error': str(e),
                'data': None,
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def _index(self) -> str:
        """メインページ（HTML）"""
        # 複数のパスを試す
        possible_paths = [
            os.path.join(os.path.dirname(__file__), 'templates', 'index.html'),
            os.path.join(os.path.dirname(__file__), '..', 'yuzutube', 'templates', 'index.html'),
            'yuzutube/templates/index.html',
            'templates/index.html',
        ]
        
        for template_path in possible_paths:
            if os.path.exists(template_path):
                try:
                    with open(template_path, 'r', encoding='utf-8') as f:
                        return f.read()
                except Exception as e:
                    print(f"Error reading {template_path}: {e}")
                    continue
        
        # フォールバック：簡易HTMLを返す
        return """
        <!DOCTYPE html>
        <html lang="ja">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>yuzutube - PHANTOM_PROTOCOL</title>
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body { 
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                    background: linear-gradient(135deg, #0f1729 0%, #1a2332 100%);
                    color: #f8fafc;
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                .container {
                    text-align: center;
                    padding: 2rem;
                    max-width: 600px;
                }
                h1 {
                    font-size: 3rem;
                    margin-bottom: 1rem;
                    background: linear-gradient(90deg, #3b82f6 0%, #8b5cf6 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                }
                p {
                    color: #94a3b8;
                    font-size: 1.1rem;
                    margin-bottom: 2rem;
                }
                .status {
                    background: rgba(59, 130, 246, 0.1);
                    border: 1px solid rgba(59, 130, 246, 0.3);
                    border-radius: 0.5rem;
                    padding: 1.5rem;
                    margin-bottom: 1rem;
                }
                .spinner {
                    display: inline-block;
                    width: 2rem;
                    height: 2rem;
                    border: 2px solid rgba(59, 130, 246, 0.2);
                    border-top-color: #3b82f6;
                    border-radius: 50%;
                    animation: spin 0.8s linear infinite;
                }
                @keyframes spin {
                    to { transform: rotate(360deg); }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🔐 yuzutube</h1>
                <p>PHANTOM_PROTOCOL v2.0.0-ULTRA</p>
                <div class="status">
                    <div class="spinner"></div>
                    <p style="margin-top: 1rem;">初期化中...</p>
                </div>
                <p style="font-size: 0.9rem; color: #64748b;">テンプレートを読み込み中です</p>
            </div>
        </body>
        </html>
        """
    
    async def _health(self) -> dict:
        """ヘルスチェック"""
        cache_stats = cache_manager.stats()
        
        return {
            'status': 'healthy',
            'service': 'yuzutube',
            'version': _config.get('version'),
            'cache': cache_stats,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def get_app(self) -> FastAPI:
        """アプリケーションを取得"""
        return self.app


# グローバルアプリケーションインスタンス
_ultra_app = _UltraApp()
app = _ultra_app.get_app()
