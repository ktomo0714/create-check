import streamlit as st

# 最初にページ設定を行う（必ず最初のStreamlit関数として呼び出す）
st.set_page_config(
    page_title="生成・校閲アプリケーション",
    page_icon="📝",
    layout="wide"
)

import os
import openai  # 古いSDK方式を使用

# OpenAI SDKバージョンを表示（デバッグ用）
try:
    st.sidebar.write(f"OpenAI SDK バージョン: {openai.__version__}")
except Exception as e:
    st.sidebar.write("OpenAI SDKバージョンを確認できません")

# Streamlit Secretsからのキー読み込み
try:
    api_key = st.secrets["OPENAI_API_KEY"]
except Exception as e:
    st.error("OpenAI APIキーがSecretsに設定されていません。Streamlit Cloudの「Secrets」メニューで設定してください。")
    st.error(f"エラー詳細: {e}")
    st.stop()

# 古いバージョンのOpenAI SDKを使用
openai.api_key = api_key

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
        "使用するモデル:",
        ["gpt-4o-mini", "gpt-4-turbo"],
        index=0
    )
    
    # 温度設定（クリエイティビティの調整）
    temperature = st.slider("温度 (クリエイティビティ)", 0.0, 1.0, 0.7, 0.1)
    
    # ストリーミング設定
    use_streaming = st.checkbox("ストリーミング表示を有効にする", value=True)
    
    st.divider()
    st.write("生成・校閲アプリケーション")

# メインコンテンツ
st.title("生成・校閲アプリケーション")

# ストリーミング処理関数
def process_openai_stream(stream, placeholder):
    """OpenAI APIからのストリームを処理し、Streamlitに表示する"""
    collected_content = ""
    for chunk in stream:
        if hasattr(chunk.choices[0], 'delta') and hasattr(chunk.choices[0].delta, 'content'):
            content_chunk = chunk.choices[0].delta.content
            if content_chunk is not None:
                collected_content += content_chunk
                placeholder.markdown(collected_content)
    return collected_content

if app_mode == "テキスト生成":
    st.header("テキスト生成")
    
    prompt_type = st.selectbox(
        "生成するテキストのタイプ:",
        ["メールマガジン", "SMS", "SNS投稿"]
    )
    
    topic = st.text_input("トピックや主題:")
    
    length = st.select_slider(
        "文章の長さ:",
        options=["短め (100字程度)", "標準 (300字程度)", "長め (500字程度)", "詳細 (1000字以上)"]
    )
    
    additional_info = st.text_area("追加情報や要望があれば入力してください:")
    
    if st.button("生成する", type="primary"):
        if not topic:
            st.warning("トピックを入力してください。")
        else:
            prompt = f"""
            次の条件に合うテキストを生成してください:
            - タイプ: {prompt_type}
            - トピック: {topic}
            - 長さ: {length}
            - 追加情報: {additional_info}
            
            日本語で自然な文章を生成してください。
            """
            
            try:
                # 結果表示用のコンテナを準備
                result_container = st.container()
                result_container.info("AIが文章を生成中...")
                output_placeholder = result_container.empty()
                
                if use_streaming:
                    # ストリーミングモードでAPI呼び出し
                    stream = openai.ChatCompletion.create(
                        model=model,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=temperature,
                        stream=True
                    )
                    
                    result = process_openai_stream(stream, output_placeholder)
                else:
                    # 非ストリーミングモードでAPI呼び出し
                    with st.spinner("AIが文章を生成中..."):
                        response = openai.ChatCompletion.create(
                            model=model,
                            messages=[{"role": "user", "content": prompt}],
                            temperature=temperature,
                        )
                        
                        result = response.choices[0].message.content
                        output_placeholder.markdown(result)
                
                # 処理完了後にステータスを更新
                result_container.success("テキストが生成されました！")
                
                # ダウンロードボタン
                st.download_button(
                    label="テキストをダウンロード",
                    data=result,
                    file_name=f"{topic}_generated_text.txt",
                    mime="text/plain"
                )
            
            except Exception as e:
                st.error(f"エラーが発生しました: {str(e)}")

elif app_mode == "テキスト校閲":
    st.header("テキスト校閲")
    
    input_text = st.text_area("校閲したいテキストを入力してください:", height=200)
    
    check_options = st.multiselect(
        "確認項目:",
        ["文法", "スペル", "景品表示法への抵触がないか", "わかりやすさ", "一貫性"]
    )
    
    if st.button("校閲する", type="primary"):
        if not input_text:
            st.warning("テキストを入力してください。")
        else:
            checks = ", ".join(check_options) if check_options else "すべての側面"
            
            prompt = f"""
            以下のテキストを校閲してください。{checks}に注目して改善点を指摘し、
            修正案を提案してください。元のテキストを尊重しつつ、より明確で効果的な表現を目指してください。
            
            テキスト:
            {input_text}
            
            以下の形式で回答してください：
            1. 全体的な評価
            2. 具体的な改善点（元の文と修正案を対比）
            3. 修正後の全文
            """
            
            try:
                # タブで表示
                tab1, tab2 = st.tabs(["校閲結果", "比較"])
                
                with tab1:
                    # 結果表示用のコンテナを準備
                    result_container = st.container()
                    result_container.info("AIが校閲中...")
                    output_placeholder = result_container.empty()
                    
                    if use_streaming:
                        # ストリーミングモードでAPI呼び出し
                        stream = openai.ChatCompletion.create(
                            model=model,
                            messages=[{"role": "user", "content": prompt}],
                            temperature=temperature,
                            stream=True
                        )
                        
                        result = process_openai_stream(stream, output_placeholder)
                    else:
                        # 非ストリーミングモードでAPI呼び出し
                        with st.spinner("AIが校閲中..."):
                            response = openai.ChatCompletion.create(
                                model=model,
                                messages=[{"role": "user", "content": prompt}],
                                temperature=temperature,
                            )
                            
                            result = response.choices[0].message.content
                            output_placeholder.markdown(result)
                    
                    # 処理完了後にステータスを更新
                    result_container.success("校閲が完了しました！")
                
                with tab2:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("元のテキスト")
                        st.text_area("", input_text, height=300)
                    with col2:
                        st.subheader("校閲後の提案")
                        # 処理が完了するまで待機
                        if 'result' in locals():
                            st.text_area("", result, height=300)
                        else:
                            st.info("校閲結果を待っています...")
            
            except Exception as e:
                st.error(f"エラーが発生しました: {str(e)}")

# フッター
st.markdown("---")
st.markdown("このアプリケーションは主としてOpenAI GPT-4o-mini APIを使用しています。生成されたテキストは参考用途にのみご利用ください。")
