"""
⚡ 究極のFastAPIアプリケーション - Vercel対応版
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from datetime import datetime
import os

# インポートエラーをキャッチ
try:
    from yuzutube.security.crypto import _crypto_engine
except Exception:
    _crypto_engine = None

try:
    from yuzutube.cache.manager import cache_manager
except Exception:
    cache_manager = None

try:
    from yuzutube.core.client import ultra_client
except Exception:
    ultra_client = None


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncGenerator:
    """アプリケーションライフサイクル"""
    print("🚀 yuzutube PHANTOM_PROTOCOL Starting...")
    yield
    print("✅ Shutdown complete")


class _SimpleApp:
    """シンプルなアプリケーション"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """初期化"""
        self.app = FastAPI(
            title="yuzutube",
            version="2.0.0-ULTRA",
            description="Phantom Protocol Media Platform",
            lifespan=_lifespan
        )
        
        # CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # ルート登録
        self._register_routes()
    
    def _register_routes(self):
        """ルート登録"""
        
        @self.app.get("/", response_class=HTMLResponse)
        async def index():
            return self._get_html()
        
        @self.app.get("/api/search")
        async def search(query: str, limit: int = 12):
            return await self._search(query, limit)
        
        @self.app.get("/api/home")
        async def home():
            return await self._get_home()
        
        @self.app.get("/api/health")
        async def health():
            return {
                'status': 'healthy',
                'service': 'yuzutube',
                'version': '2.0.0-ULTRA',
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _get_html(self) -> str:
        """HTMLを返す"""
        return """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>yuzutube - PHANTOM_PROTOCOL</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        :root {
            --primary: #0a0e27;
            --secondary: #1a1f3a;
            --accent: #3b82f6;
            --accent-dark: #8b5cf6;
            --text: #f8fafc;
            --text-secondary: #94a3b8;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0f1729 0%, #1a2332 50%, #0a1428 100%);
            color: var(--text);
            min-height: 100vh;
        }
        header {
            position: sticky;
            top: 0;
            z-index: 1000;
            background: rgba(15, 23, 42, 0.8);
            backdrop-filter: blur(12px);
            border-bottom: 1px solid rgba(71, 85, 105, 0.3);
            padding: 1rem;
        }
        .header-container {
            max-width: 1400px;
            margin: 0 auto;
            display: flex;
            align-items: center;
            gap: 1.5rem;
        }
        .logo {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            flex-shrink: 0;
        }
        .logo-icon {
            width: 2.5rem;
            height: 2.5rem;
            border-radius: 0.5rem;
            background: linear-gradient(135deg, var(--accent) 0%, var(--accent-dark) 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 1.25rem;
        }
        .logo-text {
            font-size: 1.5rem;
            font-weight: 700;
            background: linear-gradient(90deg, var(--accent) 0%, var(--accent-dark) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .search-container {
            flex: 1;
            max-width: 30rem;
        }
        .search-input {
            width: 100%;
            padding: 0.6rem 1rem;
            border-radius: 9999px;
            background: rgba(30, 41, 59, 0.8);
            border: 1px solid rgba(71, 85, 105, 0.3);
            color: var(--text);
            font-size: 0.95rem;
            transition: all 0.3s ease;
        }
        .search-input:focus {
            outline: none;
            border-color: var(--accent);
            background-color: rgba(30, 41, 59, 1);
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }
        main {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem 1rem;
        }
        .content-header h1 {
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        .content-header p {
            color: var(--text-secondary);
            font-size: 0.95rem;
        }
        .video-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 1.5rem;
            margin-top: 2rem;
        }
        .video-card {
            cursor: pointer;
            transition: transform 0.2s;
        }
        .video-card:hover {
            transform: translateY(-4px);
        }
        .video-thumbnail {
            position: relative;
            overflow: hidden;
            border-radius: 0.75rem;
            aspect-ratio: 16 / 9;
            background: rgba(30, 41, 59, 0.8);
            margin-bottom: 0.75rem;
        }
        .video-thumbnail img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.3s ease;
        }
        .video-card:hover .video-thumbnail img {
            transform: scale(1.05);
        }
        .video-title {
            font-weight: 600;
            font-size: 0.95rem;
            line-height: 1.3;
            margin-bottom: 0.5rem;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
        .video-channel {
            font-size: 0.85rem;
            color: var(--text-secondary);
            margin-bottom: 0.25rem;
        }
        .video-stats {
            font-size: 0.8rem;
            color: var(--text-secondary);
        }
        .loading {
            text-align: center;
            padding: 3rem;
            color: var(--text-secondary);
        }
        .spinner {
            display: inline-block;
            width: 2rem;
            height: 2rem;
            border: 2px solid rgba(59, 130, 246, 0.2);
            border-top-color: var(--accent);
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <header>
        <div class="header-container">
            <div class="logo">
                <div class="logo-icon">▶</div>
                <div class="logo-text">yuzutube</div>
            </div>
            <div class="search-container">
                <input
                    type="text"
                    id="searchInput"
                    class="search-input"
                    placeholder="動画を検索..."
                    onkeypress="if(event.key==='Enter') handleSearch()"
                >
            </div>
        </div>
    </header>

    <main>
        <div class="content-header">
            <h1 id="pageTitle">人気の動画</h1>
            <p id="pageDesc">新しい動画を発見しましょう</p>
        </div>

        <div id="videoGrid" class="video-grid">
            <div style="grid-column: 1/-1; text-align: center; padding: 2rem;">
                <div class="spinner"></div>
                <p style="margin-top: 1rem; color: var(--text-secondary);">読み込み中...</p>
            </div>
        </div>
    </main>

    <script>
        async function loadHome() {
            try {
                const response = await fetch('/api/home');
                const data = await response.json();
                displayVideos(data.data?.results || [], '人気の動画');
            } catch (error) {
                console.error('Error:', error);
                document.getElementById('videoGrid').innerHTML = '<div style="grid-column:1/-1;padding:2rem;text-align:center;color:#94a3b8;">動画の読み込みに失敗しました</div>';
            }
        }

        async function handleSearch() {
            const query = document.getElementById('searchInput').value.trim();
            if (!query) return;
            
            try {
                const response = await fetch(`/api/search?query=${encodeURIComponent(query)}&limit=20`);
                const data = await response.json();
                displayVideos(data.data?.results || [], `"${query}" の検索結果`);
            } catch (error) {
                console.error('Error:', error);
            }
        }

        function displayVideos(videos, title) {
            document.getElementById('pageTitle').textContent = title;
            document.getElementById('pageDesc').textContent = `${videos.length} 件の動画`;

            const grid = document.getElementById('videoGrid');
            grid.innerHTML = videos.map(v => `
                <div class="video-card">
                    <div class="video-thumbnail">
                        <img src="${v.thumbnail}" alt="${v.title}" onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22200%22 height=%22112%22%3E%3Crect fill=%23333%22/%3E%3C/svg%3E'" loading="lazy">
                    </div>
                    <div class="video-title">${v.title}</div>
                    <div class="video-channel">${v.uploader}</div>
                    <div class="video-stats">${formatViews(v.view_count)} 回視聴</div>
                </div>
            `).join('');
        }

        function formatViews(count) {
            if (!count) return '0';
            if (count >= 1000000) return (count / 1000000).toFixed(1) + 'M';
            if (count >= 1000) return (count / 1000).toFixed(1) + 'K';
            return count.toString();
        }

        window.addEventListener('DOMContentLoaded', loadHome);
    </script>
</body>
</html>"""
    
    async def _search(self, query: str, limit: int = 12) -> dict:
        """検索"""
        try:
            if ultra_client:
                data = await ultra_client.get(
                    f"https://helena-stating-families-plays.trycloudflare.com/search/{query}",
                    params={"limit": min(limit, 100)}
                )
                return {'data': data, 'timestamp': datetime.utcnow().isoformat()}
        except Exception as e:
            print(f"Search error: {e}")
        
        return {'data': {'results': []}, 'timestamp': datetime.utcnow().isoformat()}
    
    async def _get_home(self) -> dict:
        """ホーム"""
        try:
            if ultra_client:
                data = await ultra_client.get(
                    "https://helena-stating-families-plays.trycloudflare.com/search/popular",
                    params={"limit": 12}
                )
                return {'data': data, 'timestamp': datetime.utcnow().isoformat()}
        except Exception as e:
            print(f"Home error: {e}")
        
        return {'data': {'results': []}, 'timestamp': datetime.utcnow().isoformat()}
    
    def get_app(self) -> FastAPI:
        """アプリケーション取得"""
        return self.app


# グローバルインスタンス
_app = _SimpleApp()
app = _app.get_app()
