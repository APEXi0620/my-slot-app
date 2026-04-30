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
st.set_page_config(page_title="5.5スロ収支", layout="wide")

# --- デザイン設定：背景黒、入力枠白、ボタン青背景・白文字 ---
st.markdown(
    """
    <style>
    /* 背景は黒 */
    .stApp, [data-testid="stSidebar"] {
        background-color: #000000 !important;
        color: #ffffff !important;
    }
    
    /* 入力枠内は白、文字は黒 */
    input, select, textarea, div[data-baseweb="input"], div[data-baseweb="select"] {
        background-color: #ffffff !important;
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        border: none !important;
    }

    /* 【修正】記録するボタン：背景を青、文字色を白に設定 */
    .stButton>button {
        background-color: #0000ff !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        border: none !important;
    }

    /* ラベル（項目名）は白 */
    label, [data-testid="stWidgetLabel"] p {
        color: #ffffff !important;
    }

    /* 削除ボタン：背景黒、赤文字 */
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
    st.header("🎰 確率計算機")
    kaiten = st.number_input("総回転数", min_value=1, value=1000)
    big = st.number_input("BIG回数", min_value=0)
    reg = st.number_input("REG回数", min_value=0)
    if big > 0: st.write(f"BIG確率: **1/{kaiten/big:.1f}**")
    if reg > 0: st.write(f"REG確率: **1/{kaiten/reg:.1f}**")
    if (big + reg) > 0: st.info(f"合成確率: **1/{kaiten/(big+reg):.1f}**")

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
    
    # 記録するボタン
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
    st.markdown(f"### 累計トータル収支: <span style='color:{color}; font-size:32px;'>{total} 円</span>", unsafe_allow_html=True)

    col_left, col_right = st.columns(2)
    with col_left:
        st.write("### 📅 月別収支")
        def get_month(x):
            parts = x.split('/')
            if len(parts) >= 3: return str(int(parts[1])) + "月"
            if len(parts) == 2: return str(int(parts[0])) + "月"
            return "不明"
        df['月'] = df['日付'].apply(get_month)
        monthly = df.groupby('月', sort=False)['収支'].sum()
        st.bar_chart(monthly)

    with col_right:
        st.write("### 📈 機種別分析")
        summary = df.groupby('機種名').agg(平均=('収支', 'mean'), 回数=('収支', 'count'))
        summary['平均'] = summary['平均'].astype(int)
        st.table(summary)

    st.divider()
    st.write("### 📝 履歴の管理")
    for i, row in df.iloc[::-1].iterrows():
        c1, c2, c3, c4 = st.columns(4) 
        c1.write(row['日付'])
        c2.write(row['機種名'])
        c3.write(f"{row['収支']}円")
        if c4.button("削除", key=f"del_{i}"):
            df = df.drop(i)
            df.to_csv(FILENAME, index=False, encoding='utf-8-sig')
            st.rerun()
else:
    st.info("データがありません。")