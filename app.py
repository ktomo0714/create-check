import streamlit as st
import openai  # 古い方式のインポート
import os

# Streamlit Secretsからのキー読み込み
try:
    api_key = st.secrets["OPENAI_API_KEY"]
except Exception as e:
    st.error("OpenAI APIキーがSecretsに設定されていません。Streamlit Cloudの「Secrets」メニューで設定してください。")
    st.error(f"エラー詳細: {e}")
    st.stop()

# 古い方式のOpenAI API設定
openai.api_key = api_key

# アプリのタイトルとスタイル
st.set_page_config(
    page_title="生成・校閲アプリケーション",
    page_icon="📝",
    layout="wide"
)

# サイドバーメニュー
with st.sidebar:
    st.title("機能選択")
    app_mode = st.radio(
        "モードを選択してください:",
        ["テキスト生成", "テキスト校閲"]
    )
    
    st.divider()
    
    # APIモデル選択
    model = st.selectbox(
        "使用するモ
