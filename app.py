import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 設定 ---
FILENAME = 'shuushi_data.csv'
SLOT_TANKA = 5.5

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

# --- デザイン修正：記録するボタンを青背景・白文字に強制固定 ---
st.markdown(
    """
    <style>
    /* 全体の背景 */
    .stApp, [data-testid="stSidebar"] {
        background-color: #000000 !important;
        color: #ffffff !important;
    }
    
    /* 入力枠：背景白、文字黒 */
    input, div[data-baseweb="input"] {
        background-color: #ffffff !important;
        color: #000000 !important;
    }

    /* 【重要】記録するボタン：青背景・白文字 */
    div.stForm [data-testid="stFormSubmitButton"] button {
        background-color: #0000ff !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        border: none !important;
        width: 100% !important;
        font-weight: bold !important;
    }

    /* 削除ボタン：赤枠デザイン */
    div.stButton > button[kind="secondary"] {
        background-color: #000000 !important;
        color: #ff4b4b !important;
        border: 1px solid #ff4b4b !important;
    }

    /* ラベル類 */
    label, p { color: #ffffff !important; }
    </style>
    """,
    unsafe_allow_html=True
)

# --- サイドバー ---
with st.sidebar:
    st.header("🎰 確率計算機")
    kaiten = st.number_input("総回転数", min_value=1, value=1000)
    big = st.number_input("BIG回数", min_value=0)
    reg = st.number_input("REG回数", min_value=0)
    st.divider()
    if big > 0: st.write(f"BIG 1/{kaiten/big:.1f}")
    if reg > 0: st.write(f"REG 1/{kaiten/reg:.1f}")
    if (big+reg) > 0: st.info(f"合算 1/{kaiten/(big+reg):.1f}")

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
    
    submitted = st.form_submit_button("記録する")
    
    if submitted:
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
    st.dataframe(df[['日付', '機種名', '収支']].iloc[::-1], use_container_width=True)

    with st.expander("データの削除はこちら"):
        for i, row in df.iloc[::-1].iterrows():
            # カラム数を指定(2つに分割)
            col_a, col_b = st.columns([3, 1])
            col_a.write(f"{row['日付']} {row['機種名']} ({row['収支']}円)")
            if col_b.button("削除", key=f"del_{i}"):
                df = df.drop(i)
                df.to_csv(FILENAME, index=False, encoding='utf-8-sig')
                st.rerun()
else:
    st.info("データがありません。")