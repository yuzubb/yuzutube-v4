"""
🌐 Vercel Serverless Function Handler
PHANTOM_PROTOCOL FastAPI Application
"""

import sys
import os

# モジュールパスを追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from yuzutube.app import app

# Vercel用ハンドラー
handler = app
