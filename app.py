import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- 設定 ---
SLOT_TANKA = 5.5

# 全機種の設定データ (初当たり・合算確率)
SPEC_DATA = {
    "ミスタージャグラー": [163.8, 159.1, 153.8, 142.5, 131.6, 118.7],
    "アイムジャグラーEX": [168.5, 159.1, 150.3, 140.9, 135.4, 127.5],
    "マイジャグラーV": [163.8, 159.1, 155.3, 144.0, 135.4, 114.6],
    "ファンキージャグラー2": [165.1, 158.3, 145.3, 133.7, 126.3, 119.6],
    "ゴーゴージャグラー3": [149.6, 146.3, 140.3, 135.4, 126.8, 117.3],
    "ハイパーラッシュ": [173.8, 172.5, 170.2, 161.8, 151.7, 142.5],
    "新ハナビR": [156.0, 149.6, 0, 140.9, 134.8, 131.1],
    "ディスクアップ2": [182.0, 180.2, 0, 171.1, 161.0, 149.3],
    "ファミスタ回胴版！！": [182.0, 179.6, 0, 171.1, 161.8, 150.3],
    "L北斗の拳": [383.4, 370.5, 347.1, 297.8, 258.7, 235.1],
    "L押忍！番長4": [259.5, 256.3, 247.0, 227.0, 203.4, 198.8],
    "L聖闘士星矢 海皇覚醒ED": [363.3, 353.5, 335.7, 303.4, 275.9, 244.6],
    "L ToLOVEるダークネス": [355.3, 344.9, 321.7, 280.9, 255.4, 230.1],
    "L革命機ヴァルヴレイヴD": [519.0, 516.0, 490.0, 434.0, 414.0, 401.0],
    "Lモンスターハンターライズ": [309.8, 297.4, 281.3, 253.9, 233.1, 212.0],
    "LからくりサーカスG": [564.0, 543.0, 514.0, 469.0, 436.0, 409.0],
    "L炎炎ノ消防隊": [243.2, 233.7, 223.5, 201.7, 188.0, 173.8],
    "Lソードアート・オンラインB2": [412.2, 396.1, 375.0, 319.4, 286.0, 247.9],
    "LエウレカセブンHIEVO": [195.4, 191.0, 182.2, 169.1, 158.4, 143.7],
    "Lラブ嬢3M4": [252.3, 246.5, 235.1, 218.4, 198.8, 178.2],
    "Lバジリスク絆2～天膳～": [247.3, 239.9, 230.1, 206.8, 187.3, 170.3],
    "L GI優駿倶楽部黄金KD": [336.8, 328.7, 313.1, 276.4, 252.1, 219.6],
    "LキングパルサーSLCC": [151.0, 147.2, 144.5, 137.9, 131.7, 121.7],
    "Sストライク・ザ・ブラッドZC": [199.1, 195.1, 186.2, 167.3, 150.3, 133.4],
    "L戦姫絶唱シンフォギア 正義の歌": [295.0, 290.1, 281.4, 253.3, 234.3, 201.2],
    "L防振り": [319.4, 307.7, 289.4, 244.6, 221.7, 199.0],
    "Lスマスロ真北斗無双": [381.1, 372.4, 355.6, 310.3, 279.1, 248.3],
    "LゾンビランドサガA1": [164.5, 161.4, 157.0, 145.4, 133.3, 118.5],
    "Lスマスロ頭文字D2nd": [317.0, 311.2, 294.6, 258.8, 235.2, 207.2],
    "LバンドリS11": [332.3, 324.9, 311.6, 283.6, 257.7, 224.2],
    "L鬼武者3XA": [319.3, 311.1, 298.5, 272.5, 244.1, 212.1],
    "Lスマスロ 聖戦士ダンバイン": [342.3, 335.7, 321.4, 288.6, 256.4, 219.3],
    "Lありふれた職業で世界最強": [321.1, 310.5, 292.3, 256.4, 233.1, 201.9],
    "Lシン・エヴァンゲリオン": [345.5, 334.3, 312.2, 274.5, 253.1, 221.0],
    "S SHAMAN KING": [182.0, 178.5, 172.3, 155.4, 140.1, 125.5],
    "Lスマスロカイジ 狂宴": [315.4, 308.2, 291.5, 266.4, 231.0, 199.5],
    "LヨシムネS": [250.6, 243.2, 222.1, 201.4, 185.3, 166.2],
    "L麻雀物語S2": [255.4, 248.1, 231.5, 201.3, 182.1, 163.4],
    "L東京リベンジャーズ": [342.0, 334.0, 321.0, 289.0, 254.0, 218.0],
    "S咲-Saki-頂上決戦YR": [224.4, 215.1, 201.2, 188.4, 175.2, 160.1],
    "Sいろはに愛姫PA5": [158.3, 158.3, 158.3, 0, 0, 149.3],
    "L HEY！エリートサラリーマン鏡PA4": [273.1, 263.5, 251.0, 222.8, 193.0, 183.0],
    "スマスロ押忍！番長ZERO": [245.4, 237.4, 224.2, 203.1, 183.5, 169.5],
    "バイオハザード5ZE": [310.0, 295.0, 281.0, 252.0, 226.0, 193.0],
    "ルパン三世大航海者の秘宝": [188.3, 183.1, 176.2, 163.8, 149.6, 131.6],
    "ドルアーガの塔": [209.0, 198.0, 181.0, 163.0, 150.0, 135.0],
}

st.set_page_config(page_title="5.5スロ収支管理Pro", layout="wide")

# Googleスプレッドシート接続設定
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        # スプレッドシートからデータを取得 (キャッシュを無効にして最新を取得)
        data = conn.read(ttl="0s")
        return data.dropna(how="all") # 空の行を除去
    except:
        # データが空の場合の初期フレーム
        return pd.DataFrame(columns=['日付', '機種名', '投資', '回収枚数', '収支', '備考'])

# デザイン調整
st.markdown(
    """
    <style>
    .stApp, [data-testid="stSidebar"] { background-color: #000000 !important; color: #ffffff !important; }
    input, div[data-baseweb="input"], div[data-baseweb="select"], textarea {
        background-color: #ffffff !important; color: #000000 !important;
    }
    label, p, h1, h2, h3 { color: #ffffff !important; }
    div.stForm [data-testid="stFormSubmitButton"] button {
        background-color: #0000ff !important; color: #ffffff !important;
        font-weight: bold !important; width: 100% !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- サイドバー (設定推測) ---
with st.sidebar:
    st.header("🎰 設定推測・計算")
    target_model = st.selectbox("機種を選択", ["選択なし"] + sorted(list(SPEC_DATA.keys())))
    kaiten = st.number_input("総回転数", min_value=1, value=1000)
    col_b, col_r = st.columns(2)
    with col_b: s_big = st.number_input("BIG回数", min_value=0)
    with col_r: s_reg = st.number_input("REG(初当り)", min_value=0)
    
    if (s_big + s_reg) > 0:
        gassan = kaiten / (s_big + s_reg)
        st.write(f"現在の合算: **1/{gassan:.1f}**")
        if target_model != "選択なし":
            specs = SPEC_DATA[target_model]
            best_diff = 999
            likely_setting = 1
            for i, val in enumerate(specs):
                if val == 0: continue
                diff = abs(gassan - val)
                if diff < best_diff:
                    best_diff = diff
                    likely_setting = i + 1
            st.success(f"推定設定: **設定{likely_setting}** 付近")

# --- メイン画面 ---
st.title("🎰 5.5スロ 収支表 (クラウド保存版)")

df = load_data()

with st.form("input_form", clear_on_submit=True):
    st.write("### 📝 稼働を記録")
    col1, col2 = st.columns(2)
    with col1: date = st.date_input("日付", datetime.now())
    with col2: name = st.selectbox("機種名", sorted(list(SPEC_DATA.keys())) + ["その他"])
    
    if name == "その他":
        name = st.text_input("機種名を手入力")

    col3, col4 = st.columns(2)
    with col3: toushi = st.number_input("投資額(円)", min_value=0, step=500)
    with col4: maisuu = st.number_input("回収枚数(枚)", min_value=0, step=10)
    memo = st.text_area("備考 (メモ)", placeholder="設定示唆やメモなど")
    
    if st.form_submit_button("スプレッドシートに保存"):
        shuushi = int(maisuu * SLOT_TANKA) - toushi
        new_row = pd.DataFrame([[date.strftime("%m/%d"), name, toushi, maisuu, shuushi, memo]], 
                               columns=['日付', '機種名', '投資', '回収枚数', '収支', '備考'])
        
        # 既存データと結合してスプレッドシートを更新
        updated_df = pd.concat([df, new_row], ignore_index=True)
        conn.update(data=updated_df)
        st.success("Googleスプレッドシートに保存しました！")
        st.rerun()

if not df.empty:
    st.divider()
    # 収支列を数値型に変換して合計を計算
    df['収支'] = pd.to_numeric(df['収支'], errors='coerce')
    total = df['収支'].sum()
    color = "#ff4b4b" if total < 0 else "#00ff00"
    st.markdown(f"## 累計トータル収支: <span style='color:{color};'>{int(total):,} 円</span>", unsafe_allow_html=True)
    
    st.write("### 📝 履歴一覧 (最新が上)")
    st.dataframe(df.iloc[::-1], use_container_width=True, hide_index=True)
else:
    st.info("データがありません。最初の稼働を記録しましょう！")
