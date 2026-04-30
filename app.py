import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 設定 ---
FILENAME = 'shuushi_data.csv'
SLOT_TANKA = 5.5

# 6.5号機ハイパーラッシュ等の設定データ（合算確率）
SPEC_DATA = {
    "ハイパーラッシュ": [173.8, 172.5, 170.2, 161.8, 151.7, 142.5],
    "アイムジャグラーEX": [168.5, 159.1, 150.3, 140.9, 135.4, 127.5],
    "マイジャグラーV": [163.8, 159.1, 155.3, 144.0, 135.4, 114.6],
    "ファンキージャグラー2": [165.1, 158.3, 145.3, 133.7, 126.3, 119.6],
    "ゴーゴージャグラー3": [149.6, 146.3, 140.3, 135.4, 126.8, 117.3],
}

def load_data():
    if os.path.exists(FILENAME):
        try:
            df = pd.read_csv(FILENAME, encoding='utf-8-sig')
        except:
            df = pd.read_csv(FILENAME, encoding='shift-jis')
        df['日付'] = df['日付'].fillna('').astype(str)
        return df
    return pd.DataFrame(columns=['日付', '機種名', '投資', '回収枚数', '収支'])

# 画面設定
st.set_page_config(page_title="5.5スロ収支管理", layout="wide")

# --- デザイン設定 ---
st.markdown(
    """
    <style>
    .stApp, [data-testid="stSidebar"] {
        background-color: #000000 !important;
        color: #ffffff !important;
    }
    input, div[data-baseweb="input"], div[data-baseweb="select"] {
        background-color: #ffffff !important;
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        border: none !important;
    }
    div.stForm [data-testid="stFormSubmitButton"] button {
        background-color: #0000ff !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        border: none !important;
        width: 100% !important;
        font-weight: bold !important;
    }
    label, p { color: #ffffff !important; }
    div.stButton > button[kind="secondary"] {
        background-color: #000000 !important;
        color: #ff4b4b !important;
        border: 1px solid #ff4b4b !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- サイドバー ---
with st.sidebar:
    st.header("🎰 設定推測・計算")
    target_model = st.selectbox("機種を選択", ["選択なし"] + list(SPEC_DATA.keys()))
    kaiten = st.number_input("総回転数", min_value=1, value=1000)
    big = st.number_input("BIG回数", min_value=0)
    reg = st.number_input("REG回数", min_value=0)
    
    st.divider()
    if (big + reg) > 0:
        gassan = kaiten / (big + reg)
        st.write(f"現在の合算: **1/{gassan:.1f}**")
        if target_model != "選択なし":
            specs = SPEC_DATA[target_model]
            best_diff = 999
            likely_setting = 1
            for i, val in enumerate(specs):
                diff = abs(gassan - val)
                if diff < best_diff:
                    best_diff = diff
                    likely_setting = i + 1
            st.success(f"推定設定: **設定{likely_setting}** 付近")

# --- メイン画面 ---
st.title("🎰 5.5スロ収支表")

with st.form("input_form", clear_on_submit=True):
    st.write("### 📝 稼働を記録")
    col1, col2 = st.columns(2)
    with col1: date = st.date_input("日付", datetime.now())
    with col2: name = st.text_input("機種名")
    col3, col4 = st.columns(2)
    with col3: toushi = st.number_input("投資額(円)", min_value=0, step=500)
    with col4: maisuu = st.number_input("回収枚数(枚)", min_value=0, step=10)
    
    if st.form_submit_button("記録する"):
        df = load_data()
        shuushi = int(maisuu * SLOT_TANKA) - toushi
        new_row = pd.DataFrame([[date.strftime("%m/%d"), name, toushi, maisuu, shuushi]], 
                               columns=['日付', '機種名', '投資', '回収枚数', '収支'])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(FILENAME, index=False, encoding='utf-8-sig')
        st.rerun()

df = load_data()

if not df.empty:
    st.divider()
    total = df['収支'].sum()
    color = "#ff4b4b" if total < 0 else "#00ff00"
    st.markdown(f"## 累計トータル収支: <span style='color:{color};'>{total} 円</span>", unsafe_allow_html=True)
    
    st.write("### 📝 履歴一覧")
    # 警告対策： width="stretch" に変更
    st.dataframe(df[['日付', '機種名', '収支']].iloc[::-1], width=1000)
    
    with st.expander("データの削除はこちら"):
        for i, row in df.iloc[::-1].iterrows():
            c1, c2 = st.columns([3, 1])
            c1.write(f"{row['日付']} {row['機種名']} ({row['収支']}円)")
            if c2.button("削除", key=f"del_{i}"):
                df = df.drop(i)
                df.to_csv(FILENAME, index=False, encoding='utf-8-sig')
                st.rerun()
else:
    st.info("データがありません。")