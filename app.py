import os
# import io
import json
# import html
import streamlit as st
from google import genai  # Gemini API client
from dotenv import load_dotenv  # Load .env
# from fpdf import (
#     FPDF,
#     HTMLMixin,
#     fpdf,
# )  # PDF generation with HTML support
# from mistletoe import markdown as md_to_html  # Markdown → HTML
from streamlit.components.v1 import html as st_html


st.set_page_config(page_title="MinuteGem", layout="wide")

# Inject custom sidebar width via HTML using components.html
st_html(
    """
<style>
section[data-testid='stSidebar'] > div:first-child {
    width: 400px;
}
section[data-testid='stSidebar'] {
    min-width: 400px;
}
</style>
""",
    height=0,
)


# Load environment variables
load_dotenv()

# Retrieve API key
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    st.error("環境変数 GEMINI_API_KEY が設定されていません。")
    st.stop()

# Load initial participants from env (JSON)
env_participants = os.getenv("PARTICIPANTS")
initial_participants = []
if env_participants:
    try:
        initial_participants = json.loads(env_participants)
    except json.JSONDecodeError:
        st.warning(
            '環境変数 PARTICIPANTS の形式が不正です。JSON形式で定義してください。例: [{"name":"Aさん","role":"役割","remark":"備考"}]'
        )

# Initialize Gemini client
client = genai.Client(api_key=API_KEY)

# Initialize session state for participants and generated content
if "participants" not in st.session_state:
    st.session_state.participants = initial_participants.copy()
if "minutes_md" not in st.session_state:
    st.session_state.minutes_md = None
# if "minutes_html" not in st.session_state:  # PDF生成用にHTMLも保存
#     st.session_state.minutes_html = None

# Sidebar: settings
with st.sidebar:
    st.header("アプリ設定")
    # System prompt
    st.subheader("システムプロンプト")
    system_prompt = st.text_area(
        "",
        value="""あなたは議事録作成のプロフェッショナルです。
会議で議論された主要なトピックと決定事項を要約し、誰が読んでも会議の内容が理解できる議事録を作成できます。

# 制約条件
・文字起こしデータは AI によるもので、一部の書き起こしミスが含まれています。文脈を理解し、内容を整理してください。
・基本情報（日時、場所、出席者など）を最初に記載してください。
・主要な決定事項を冒頭でまとめてください。
・次にアクションアイテムをまとめてください。
・各議題ごとに見出しを設け、発言者の名前（さん付け）と内容を記録してください。
・見出しや箇条書きで検索しやすく構造化してください。
・専門用語は初回に定義、ケバ取り、簡潔明瞭に記述してください。
・議事録部分のみを出力してください。
""",
        height=250,
    )
    # Participant form
    st.subheader("参加者設定")
    with st.form("participant_form", clear_on_submit=True):
        name = st.text_input("参加者名")
        role = st.text_input("役割")
        remark = st.text_input("備考")
        if st.form_submit_button("Add"):
            if name:
                st.session_state.participants.append(
                    {"name": name, "role": role, "remark": remark}
                )
            else:
                st.warning("参加者名を入力してください。")


# Main area
st.title("【MinuteGem】")
st.subheader("LLMによる議事録作成アプリ")

st.caption("※研究用のため、特定のアカウントからのアクセスのみ許可しています。")
st.caption("※LLMのリミットレートを超過した場合、使用不可となります。")

transcript = st.text_area("文字起こしテキストを貼り付けてください", height=300)

if st.session_state.participants:
    st.subheader("登録済み参加者")
    for idx, p in enumerate(st.session_state.participants, start=1):
        st.write(f"{idx}. {p['name']} （{p['role']}）: {p['remark']}")

# 議事録作成ボタン押下時の処理
if st.button("議事録作成"):
    if not transcript:
        st.warning("文字起こしテキストを入力してください。")
    else:
        with st.spinner("生成中…"):
            participants_text = "\n".join(
                [
                    f"- {p['name']}：役割 {p['role']}、備考 {p['remark']}"
                    for p in st.session_state.participants
                ]
            )
            prompt = (
                f"## システムプロンプト: \n{system_prompt}\n\n## 参加者: \n{participants_text}\n\n文字起こしテキスト:\n\n"
                + transcript
            )
            try:
                response = client.models.generate_content(
                    model="gemini-2.0-pro-exp-02-05",
                    contents=[prompt],
                )
                minutes_md = response.text
                # 生成結果をsession stateに保存
                st.session_state.minutes_md = minutes_md
                # # Markdown → HTML に変換してsession stateに保存
                # html_content = md_to_html(minutes_md)
                # html_content = html.unescape(html_content)  # エスケープ解除
                # st.session_state.minutes_html = html_content

            except Exception as e:
                st.error(f"LLM生成中にエラーが発生しました: {e}")
                # エラー時はsession stateをクリア
                st.session_state.minutes_md = None
                # st.session_state.minutes_html = None


# 議事録データがsession stateに存在する場合のみ表示とダウンロードボタンを出す
if st.session_state.minutes_md is not None:
    st.subheader("生成結果（Markdown）")
    st.code(st.session_state.minutes_md, language="markdown")
    st.info("右上のコピーアイコンでテキストをコピーできます。")

    # # デバッグ用: 生成されたHTMLを表示
    # with st.expander("生成されたHTMLを確認 (デバッグ用)"):
    #     st.code(st.session_state.minutes_html, language="html")

    # # PDF 用クラス定義 (ここでも良いし、もう少し上に移動しても良い)
    # class PDF(FPDF, HTMLMixin):
    #     def unescape(self, txt):
    #         return html.unescape(txt)

    # pdf = PDF()

    # # フォント設定 (PDF生成が必要な場合のみ実行)
    # try:
    #     # 使用する日本語フォントファイルのパスを指定
    #     font_path_regular = "./fonts/BIZUDPGothic-Regular.ttf"  # 標準体
    #     font_path_bold = "./fonts/BIZUDPGothic-Bold.ttf"  # 太字

    #     # フォントファイルが存在するか確認
    #     if not os.path.exists(font_path_regular) or not os.path.exists(font_path_bold):
    #         st.error(
    #             "PDF生成に必要なフォントファイルが見つかりません。以下のファイルを確認してください:"
    #         )
    #         st.error(f" - 標準体: {font_path_regular}")
    #         st.error(f" - 太字: {font_path_bold}")
    #         # フォントがない場合はPDF関連の処理を中断
    #         # st.stop() # アプリ全体ではなくPDF生成のみを中断したい場合
    #         # 以下にPDF生成処理をスキップするロジックを追加
    #         pdf_error = True  # PDF生成エラーフラグを立てる
    #     else:
    #         pdf_error = False  # PDF生成エラーフラグをリセット

    #         # 標準体フォントを fpdf に追加 (ファミリー名: "japanese", スタイル: 標準 (""))
    #         pdf.add_font("japanese", "", font_path_regular, uni=True)

    #         # 太字フォントを fpdf に追加 (ファミリー名: 標準体と同じ "japanese", スタイル: 太字 ("B"))
    #         pdf.add_font("japanese", "B", font_path_bold, uni=True)

    #         # PDF全体のデフォルトフォントを、追加した日本語フォントファミリーに設定
    #         pdf.set_font(
    #             "japanese", size=12
    #         )  # ファミリー名: "japanese", スタイル: 標準 (デフォルト)

    # except Exception as e:
    #     st.error(f"PDFフォント設定中にエラーが発生しました: {e}")
    #     # st.stop() # アプリ全体ではなくPDF生成のみを中断したい場合
    #     pdf_error = True  # PDF生成エラーフラグを立てる

    # pdf.add_page()
    # pdf.set_auto_page_break(auto=True, margin=15)

    # if not pdf_error:
    #     try:
    #         # HTMLコンテンツを書き込み (session stateから取得)
    #         pdf.write_html(st.session_state.minutes_html)

    #     except fpdf.FPDFException as e:
    #         st.error(f"PDF書き込み中にエンコーディングエラーが発生しました: {e}")
    #         st.error(
    #             "設定した日本語フォントでも表示できない文字が含まれている可能性があります。"
    #         )
    #         # st.stop()
    #         pdf_error = True
    #     except Exception as e:
    #         st.error(f"PDF生成中に予期せぬエラーが発生しました: {e}")
    #         # st.stop()
    #         pdf_error = True

    #     # PDFをバイトデータとして出力 (エラーがなければ実行)
    #     if not pdf_error:
    #         try:
    #             buffer = io.BytesIO()
    #             pdf.output(buffer)
    #             buffer.seek(0)

    #             # PDFダウンロードボタン (エラーがなければ表示)
    #             st.download_button(
    #                 "PDFでダウンロード",
    #                 data=buffer,
    #                 file_name="minutes.pdf",
    #                 mime="application/pdf",
    #             )

    #         except Exception as e:
    #             st.error(f"PDFの出力処理中にエラーが発生しました: {e}")
    #             # st.stop() # アプリ全体ではなくPDF生成のみを中断したい場合
    #             # この時点では既にエラーメッセージは出ているので、特にここでエラーフラグを立てる必要はないが整合性のため
    #             pass  # エラーメッセージは既に出ている
