# MinuteGem

Streamlit app for automatically generating meeting minutes using the Gemini API.

## 前提条件

- Python 3.8 以上（**推奨: Python 3.11**）
- `uv` パッケージマネージャーを使用してパッケージ管理を行う
- `.env` ファイルから環境変数を読み込むために `python-dotenv` を利用

## セットアップ手順

1. リポジトリをクローン

   ```bash
   git clone https://github.com/yourusername/minutegem.git
   cd minutegem
   ```

2. Python 3.11 を使用した仮想環境を作成

   - Python 3.11 をインストール（[https://www.python.org/downloads/release/python-3110/](https://www.python.org/downloads/release/python-3110/)）
   - 以下のコマンドで仮想環境を作成：
     ```bash
     uv venv --python=python3.11
     .venv\Scripts\activate  # Windows
     # または
     source .venv/bin/activate  # macOS/Linux
     ```

3. 依存パッケージのインストール

   ```bash
   uv pip install streamlit google-generativeai python-dotenv markdown2 pdfkit mistletoe fpdf
   ```

4. Gemini API キーの発行と設定

   - ブラウザで以下の URL にアクセスして API キーを取得：
     [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
   - プロジェクトルートに `.env` ファイルを作成し、以下を記述：

     ```env
     GEMINI_API_KEY=あなたの_gemini_api_key_
     ```

   - もしくはシェル上で直接設定：

     ```bash
     export GEMINI_API_KEY="あなたの_gemini_api_key_"
     # Windows (PowerShell)
     setx GEMINI_API_KEY "あなたの_gemini_api_key_"
     ```

   - ※「PARTICIPANTS」を設定することで、初期表示時から指定の参加者を表示できます。

     ```bash
     PARTICIPANTS=[{"name":"メンバーA","role":"進行役","remark":"チームリーダー"},{"name":"メンバーB","role":"〇〇アプリ開発リーダー","remark":""},{"name":"メンバーC","role":"〇〇アプリ開発メンバー","remark":""}]
     ```

5. アプリを実行

   ```bash
   streamlit run app.py
   ```

## ファイル構成

- `app.py` : Streamlit アプリ本体の Python コード
- `README.md` : 本ドキュメント
- `.env` : 環境変数を定義（Git 管理対象外）
- `uv.toml` : `uv` プロジェクト設定ファイル
- `uv.lock` : 依存関係ロックファイル

---

**Python/Streamlit Tips**

- Python 3.12 では `google-generativeai` に関する ImportError が発生する場合があります。仮想環境で Python 3.11 を使用することで解決できます。
