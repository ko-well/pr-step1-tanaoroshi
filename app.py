import streamlit as st
import google.generativeai as genai

# --- ページ設定とデザイン ---
st.set_page_config(page_title="ゼロから始める！キャリアの棚卸しアシスタント", layout="wide")

# --- カスタムCSS（壁紙・明朝体・桜色テーマ・スマホ対応） ---
st.markdown("""
<style>
/* 1. 全体のフォントを游明朝に統一（アイコン崩れ防止のため span は除外） */
html, body, p, div, a, button, h1, h2, h3, h4, h5, h6, label {
    font-family: 'Yu Mincho', '游明朝', 'YuMincho', 'Hiragino Mincho ProN', 'HGS明朝E', serif !important;
}

/* 2. ページ全体の壁紙（和紙風テクスチャ） */
.stApp {
    background-color: #FCFAFA;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' opacity='0.04'/%3E%3C/svg%3E");
    background-attachment: fixed;
}

/* 3. ヘッダーデザイン（PC用） */
.header-box {
    text-align: center;
    padding: 3rem 1rem;
    background-color: rgba(255, 255, 255, 0.8);
    border-bottom: 2px solid #DB90A0;
    margin-bottom: 2rem;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.02);
}
.header-title { font-size: 2.2rem; font-weight: 700; color: #3D2D2E; }
.header-subtitle { font-size: 1.1rem; color: #5C4B4D; margin-top: 0.8rem; line-height: 1.6; }

/* 4. 各種コンテナ・ボックスのデザイン */
div[data-testid="stForm"] {
    background-color: rgba(255, 255, 255, 0.9) !important;
    border-radius: 8px !important;
    padding: 30px !important;
    box-shadow: 0 4px 15px rgba(0,0,0,0.03) !important;
}
.ai-box {
    background-color: #FDFEFE;
    padding: 25px;
    border-radius: 8px;
    border-left: 5px solid #DB90A0;
    margin-bottom: 20px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.02);
    font-size: 1.05rem;
    line-height: 1.8;
}
.result-box {
    background-color: rgba(255, 255, 255, 0.7);
    padding: 25px;
    border-radius: 8px;
    border: 2px solid #EAE1E3;
    margin-bottom: 20px;
    font-size: 1.05rem;
    line-height: 1.8;
}

h1, h2, h3 { color: #3D2D2E !important; }

/* 5. スマートフォン向けの画面表示設定（レスポンシブ対応） */
@media screen and (max-width: 768px) {
    .header-title { font-size: 1.5rem !important; }
    .header-subtitle { font-size: 0.95rem !important; margin-top: 0.8rem !important; }
    .header-box { padding: 2rem 1rem !important; }
    
    div[data-testid="stForm"] { padding: 15px !important; }
    .ai-box, .result-box { padding: 15px !important; font-size: 0.95rem !important; }
    
    h2 { font-size: 1.3rem !important; }
    h3 { font-size: 1.1rem !important; margin-bottom: 0.5rem !important; }
    p, label { font-size: 0.95rem !important; line-height: 1.6 !important; }
    
    /* スマホ用ボタン調整（横幅いっぱい） */
    [data-testid="stFormSubmitButton"] button, 
    .stButton button, 
    [data-testid="stLinkButton"] a {
        padding: 0.6rem 1rem !important;
        font-size: 1rem !important;
        width: 100% !important;
        text-align: center;
        margin-bottom: 10px !important;
    }
}

/* 6. ボタンのデザイン（PC用ベース） */
[data-testid="stFormSubmitButton"] button, 
.stButton button,
[data-testid="stLinkButton"] a {
    background-color: #DB90A0 !important;
    color: #ffffff !important;
    border-radius: 6px !important;
    padding: 0.7rem 3rem !important;
    font-size: 1.1rem !important;
    font-weight: 600 !important;
    width: 100% !important;
    text-align: center;
    text-decoration: none !important;
    transition: all 0.3s ease;
}
[data-testid="stFormSubmitButton"] button:hover,
.stButton button:hover,
[data-testid="stLinkButton"] a:hover {
    background-color: #C27082 !important;
    transform: translateY(-2px);
}
[data-testid="stLinkButton"] a * {
    color: #ffffff !important;
}
</style>
""", unsafe_allow_html=True)

# --- タイトル表示 ---
st.markdown('''
<div class="header-box">
    <div class="header-title">🌱 ゼロから始める！キャリアの棚卸しアシスタント</div>
    <div class="header-subtitle">
        <b>【自己PR作成ステップ1：素材を集めよう】</b><br>
        ジョブカード（様式2）の内容をそのまま貼り付けるだけでOKです！<br>AIと一緒に、あなたの中に眠っている強みを発掘しましょう。
    </div>
</div>
''', unsafe_allow_html=True)

# --- セッション状態（アプリの記憶）の初期化 ---
if "step" not in st.session_state:
    st.session_state.step = 1
if "ai_first_response" not in st.session_state:
    st.session_state.ai_first_response = ""
if "final_sheet" not in st.session_state:
    st.session_state.final_sheet = ""
if "user_initial_input" not in st.session_state:
    st.session_state.user_initial_input = ""

# --- サイドバー：APIキー設定 ---
st.sidebar.header("🔑 セキュリティ設定")
api_key = st.sidebar.text_input("Gemini APIキー", type="password")

# ==========================================
# 【ステップ1】経歴の入力画面
# ==========================================
if st.session_state.step == 1:
    st.subheader("1. これまでの経験を入力してください")
    st.write("※最大3社（3業務）まで入力できます。1つだけでも大丈夫です。")
    
    with st.form("inventory_form"):
        # 複数入力用のレイアウト（タブ機能）
        tab1, tab2, tab3 = st.tabs(["🏢 1社目（または1つ目の業務）", "🏢 2社目", "🏢 3社目"])
        
        with tab1:
            period_1 = st.text_input("在籍期間（例：約3年，半年など）", key="p1")
            job_card_1 = st.text_area("様式２ 職務経歴シートの「職務内容」「学んだこと・知識技術等」のテキストをコピーして貼り付けてください", key="j1")
            hardship_1 = st.text_area("一番苦労したこと・工夫したこと（任意）", placeholder="失敗から立て直した経験なども立派な素材になります！", key="h1")
        with tab2:
            period_2 = st.text_input("在籍期間（例：約2年など）", key="p2")
            job_card_2 = st.text_area("ジョブカードの内容", height=150, key="j2")
            hardship_2 = st.text_area("一番苦労したこと・工夫したこと（任意）", key="h2")
        with tab3:
            period_3 = st.text_input("在籍期間", key="p3")
            job_card_3 = st.text_area("ジョブカードの内容", height=150, key="j3")
            hardship_3 = st.text_area("一番苦労したこと・工夫したこと（任意）", key="h3")
            
        submit_btn = st.form_submit_button("AIに強みを発掘してもらう ✨")
        
    if submit_btn:
        if not api_key:
            st.error("⚠️ 左側のメニューにAPIキーを入力してください。")
        elif not job_card_1:
            st.warning("⚠️ 最低でも「1社目」のジョブカード内容は入力してください。")
        else:
            # 入力内容をまとめる
            combined_input = f"""
            【1社目】期間: {period_1} / 職務内容等: {job_card_1} / 苦労・工夫: {hardship_1}
            【2社目】期間: {period_2} / 職務内容等: {job_card_2} / 苦労・工夫: {hardship_2}
            【3社目】期間: {period_3} / 職務内容等: {job_card_3} / 苦労・工夫: {hardship_3}
            """
            st.session_state.user_initial_input = combined_input

            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')

            prompt1 = f"""
            あなたは温かく寄り添うキャリアコンサルタントです。求職者の経歴情報から、自己PRの素材を発掘してください。
            【求職者の入力情報】
            {combined_input}

            【出力要件（以下の3点を含めて温かいトーンで出力）】
            1. 事実の整理：入力内容を「役割」「行動」「結果」の3要素に分かりやすく整理してください。
            2. 強みの発見と称賛：この経験に隠れている「ポータブルスキル（強み・技術）」を3つ提示し、なぜそう言えるのかを褒めながら解説してください。
            3. 深掘りの質問：自己PRの素材としてさらに磨きをかけるため、具体的な「行動」や「工夫」について、求職者が答えやすい深掘り質問を2〜3個だけ提示してください。
            """
            with st.spinner('AIがあなたの経験を分析し、強みを探しています...'):
                try:
                    response = model.generate_content(prompt1)
                    st.session_state.ai_first_response = response.text
                    st.session_state.step = 2
                    st.rerun()
                except Exception as e:
                    st.error(f"エラーが発生しました。詳細: {e}")

# ==========================================
# 【ステップ2】AIとの対話＆最終整理画面
# ==========================================
elif st.session_state.step == 2:
    st.success("分析が完了しました！以下のAIからのメッセージを確認し、質問に答えてみましょう。")
    
    st.markdown("<div class='ai-box'>", unsafe_allow_html=True)
    st.markdown(st.session_state.ai_first_response)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.subheader("💬 AIからの質問に答えてみましょう")
    st.write("※箇条書きでも、思いつくままの短い言葉でも大丈夫です。難しければ「特になし」でも構いません。")
    
    with st.form("deepdive_form"):
        user_answer = st.text_area("ここへ回答を入力してください", height=150)
        
        col1, col2 = st.columns(2)
        with col1:
            submit_deepdive = st.form_submit_button("最終整理シートを作成する 📝")
        with col2:
            reset_btn = st.form_submit_button("⬅️ 最初からやり直す")
            
    if reset_btn:
        st.session_state.step = 1
        st.rerun()
        
    if submit_deepdive:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt2 = f"""
        あなたはキャリアコンサルタントです。先ほどの分析結果と、求職者の追加回答を統合し、「キャリアの棚卸し完了シート」を作成してください。
        
        【初期入力情報】{st.session_state.user_initial_input}
        【AIの一次分析】{st.session_state.ai_first_response}
        【求職者の追加回答】{user_answer}
        
        【出力要件（このシートがそのまま「資料1」になります）】
        以下の項目を見出しとして、分かりやすく整理されたレポート形式で出力してください。
        ・これまでの経験のサマリー（役割・行動・結果）
        ・発掘された3つの強み・ポータブルスキル
        ・追加回答から見えた、あなたならではの「具体的なエピソード（STAR法の種）」
        ・キャリアコンサルタントからの応援メッセージ
        """
        with st.spinner('最終整理シートを作成しています...'):
            try:
                response = model.generate_content(prompt2)
                st.session_state.final_sheet = response.text
                st.session_state.step = 3
                st.rerun()
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")

# ==========================================
# 【ステップ3】完成・ダウンロード画面
# ==========================================
elif st.session_state.step == 3:
    st.success("🎉 キャリアの棚卸しシート（資料1）が完成しました！")
    
    st.warning("⚠️ 次の「自己PR作成ステップ2：キャリア・アンカー診断」でこの資料を使用します。必ず下のボタンからダウンロードして保存してください。")
    
    st.markdown("<div class='result-box'>", unsafe_allow_html=True)
    st.markdown(st.session_state.final_sheet)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.download_button(
        label="📝 この棚卸しシート（資料1）をダウンロードする",
        data=st.session_state.final_sheet,
        file_name="career_inventory_sheet1.txt",
        mime="text/plain"
    )
    
    st.write("")
    if st.button("⬅️ 最初からやり直す（データはリセットされます）"):
        st.session_state.step = 1
        st.session_state.ai_first_response = ""
        st.session_state.final_sheet = ""
        st.session_state.user_initial_input = ""
        st.rerun()

# --- ポータルサイトへ戻るボタン ---
st.markdown("---")
st.link_button("🏠 C.HARIGOMA キャリア支援ポータルへ戻る", "https://harigoma-career.streamlit.app/")
