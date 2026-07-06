# 📁 yuzutube - プロジェクト構造

## ツリー構造

```
yuzutube/
│
├── 📄 main.py                    ★ エントリーポイント（起動用）
├── 📄 requirements.txt           ★ Python依存パッケージ
├── 📄 vercel.json               ★ Vercel設定
├── 📄 .gitignore                ★ Git除外設定
├── 📄 README.md                 ★ プロジェクトドキュメント
│
├── 📁 app/                       ← メインアプリケーション
│   ├── 📄 __init__.py           # パッケージ初期化
│   ├── 📄 config.py             # ⚙️  設定ファイル
│   ├── 📄 main.py               # ⚡ FastAPIインスタンス
│   │
│   ├── 📁 routes/               # エンドポイント定義
│   │   ├── 📄 __init__.py
│   │   ├── 📄 api.py            # 📡 APIエンドポイント
│   │   └── 📄 pages.py          # 📄 ページエンドポイント
│   │
│   ├── 📁 templates/            # HTML テンプレート
│   │   ├── 📄 __init__.py
│   │   └── 📄 index.html        # 🎨 メインページ
│   │
│   └── 📁 utils/                # ユーティリティ
│       ├── 📄 __init__.py
│       └── 📄 helpers.py        # 🛠️  ヘルパー関数
│
└── 📁 api/                       # Vercelサーバーレス関数
    └── 📄 index.py             # 🌐 Vercelハンドラー
```

---

## 📊 ファイル構成と役割

### 🔴 重要なファイル（★マーク）

| ファイル | 説明 |
|---------|------|
| `main.py` | サーバー起動スクリプト（ローカル開発用） |
| `requirements.txt` | Python依存パッケージリスト |
| `vercel.json` | Vercelデプロイ設定 |
| `.gitignore` | Git管理除外設定 |
| `README.md` | プロジェクトドキュメント |

### 🟡 アプリケーションコア（app/）

| ファイル | 説明 |
|---------|------|
| `app/config.py` | API URL、ポート、キャッシュサイズなど設定 |
| `app/main.py` | FastAPIインスタンス作成、ミドルウェア設定 |

### 🟢 ルート定義（app/routes/）

| ファイル | 説明 |
|---------|------|
| `app/routes/api.py` | `/api/search`, `/api/home` など全APIエンドポイント |
| `app/routes/pages.py` | `/`, `/api/info` などHTML返却エンドポイント |

### 🔵 その他

| ファイル | 説明 |
|---------|------|
| `app/templates/index.html` | メインUIテンプレート（TailwindCSS） |
| `app/utils/helpers.py` | `format_duration()`, `fetch_from_api()` など |
| `api/index.py` | Vercel用ハンドラー（自動呼び出し） |

---

## 🎯 起動フロー

```
1. python main.py
   ↓
2. main.py から app.main インポート
   ↓
3. FastAPIインスタンス作成
   ↓
4. routes (api.py, pages.py) 登録
   ↓
5. uvicorn で localhost:8000 起動
   ↓
6. ブラウザで http://localhost:8000 アクセス
   ↓
7. index.html が読み込まれる
   ↓
8. JavaScriptが /api/* エンドポイント呼び出し
```

---

## 📝 各ファイルの目的

### `app/config.py`
**設定の一元管理**
```python
EXTERNAL_API = "https://helena-stating-families-plays.trycloudflare.com"
API_LIMIT_DEFAULT = 12
PORT = 8000
```

### `app/routes/api.py`
**APIエンドポイント定義**
```python
@router.get("/search")
async def search(query: str, limit: int = 12):
    # 外部APIを呼び出して動画検索
    data = await fetch_from_api(f"/search/{query}")
    # JSON返却
    return {"videos": [...]}`
```

### `app/routes/pages.py`
**HTML返却**
```python
@router.get("/", response_class=HTMLResponse)
async def index():
    # templates/index.html を読み込んで返却
    with open("app/templates/index.html") as f:
        return f.read()
```

### `app/templates/index.html`
**フロントエンドUI**
- Tailwind CSS で スタイリング
- バニラ JavaScript で `/api/*` を呼び出し
- グリッド表示、検索、モーダル機能

### `app/utils/helpers.py`
**共有関数**
```python
async def fetch_from_api(endpoint: str):
    # httpx で外部API呼び出し
    
def format_views(count: int):
    # 1000000 → "1.0M"
```

---

## 🔄 データフロー

```
ブラウザ
  ↓ (GET /)
フロントエンド (index.html)
  ↓ (fetch /api/search?query=python)
FastAPI
  ├→ app/main.py (FastAPIインスタンス)
  ├→ app/routes/api.py (エンドポイント処理)
  └→ app/utils/helpers.py (fetch_from_api)
      ↓
    外部API (helena-stating-families-plays.trycloudflare.com)
      ↓ (JSON応答)
    app/utils/helpers.py
      ↓
    app/routes/api.py
      ↓ (JSON返却)
ブラウザ (JavaScript で受け取り)
  ↓
画面にカード表示
```

---

## 🚀 デプロイ時の流れ

### ローカル開発
```bash
python main.py
# uvicorn で localhost:8000 起動
```

### Vercel デプロイ
```
GitHub push
  ↓
Vercel が git clone
  ↓
pip install -r requirements.txt
  ↓
api/index.py を サーバーレス関数として実行
  ↓
FastAPI が動作
  ↓
https://your-project.vercel.app で公開
```

---

## 📌 重要なポイント

1. **config.py で設定一元化**
   - API URL を変更する場合は config.py のみ編集

2. **複数ファイル構成**
   - 保守性向上
   - テストしやすい
   - スケーラビリティ

3. **非同期処理**
   - `async def` で複数リクエスト同時処理

4. **CORS対応**
   - フロントエンドからのクロスオリジンリクエスト許可

5. **ローカル ＋ Vercel 両対応**
   - `main.py`: ローカル開発
   - `api/index.py`: Vercelデプロイ

---

**Happy coding! 🎬**
