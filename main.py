#!/usr/bin/env python3
"""
🎥 yuzutube PHANTOM_PROTOCOL - エントリーポイント
究極の難読化型アプリケーション
"""

import sys
import os

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from yuzutube.app import app
import uvicorn

# Vercel用ハンドラー
handler = app

if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════╗
    ║   🔐 PHANTOM_PROTOCOL INITIALIZED       ║
    ║   yuzutube v2.0.0 ULTRA                 ║
    ║   Starting at http://localhost:8000     ║
    ╚══════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        "yuzutube.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
