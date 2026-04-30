import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 設定 ---
FILENAME = 'shuushi_data.csv'
SLOT_TANKA = 5.5

# データの読み込み関数
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

# --- 背景を黒・文字を白に固定するデザイン設定 ---
st.markdown(
    """
    <style>
    /* 全体の背景色と文字色 */
    .stApp {
        background-color: #000000;
        color: #ffffff;
    }
    /* 入力欄やボタンの見た目調整 */
    input, select, textarea {
        color: #ffffff !important;
    }
    .stButton>button {
        background-color: #333333;
        color: #ffffff;
        border-radius: 5px;
    }
    /* 履歴の削除ボタンを赤っぽく */
    button[kind="secondary"] {
        color: #ff4b4b !important;
        border-color: #ff4b4b !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- サイドバー：確率計算機 ---
with st.sidebar:
    st.header("🎰 確率計算機")
    kaiten = st.number_input("総回転数", min_value=1, value=1000)
    big = st.number_input("BIG回数", min_value=0)
    reg = st.number_input("REG回数", min_value=0)
    st.divider()
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
    
    if st.form_submit_button("記録する"):
        df = load_data()
        shuushi = int(maisuu * SLOT_TANKA) - toushi
        new_row = pd.DataFrame([[date.strftime("%m/%d"), name, toushi, maisuu, shuushi]], 
                               columns=['日付', '機種名', '投資', '回収枚数', '収支'])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(FILENAME, index=False, encoding='utf-8-sig')
        st.success(f"記録完了！ 収支: {shuushi}円")
        st.rerun()

df = load_data()

if not df.empty:
    st.divider()
    # 累計収支を大きく表示
    total = df['収支'].sum()
    color = "#ff4b4b" if total < 0 else "#00ff00"
    st.markdown(f"### 累計トータル収支: <span style='color:{color}; font-size:32px;'>{total} 円</span>", unsafe_allow_html=True)

    col_left, col_right = st.columns(2)
    with col_left:
        st.write("### 📅 月別収支")
        def get_month(x):
            if '/' in x: return x.split('/')[0] + "月"
            if len(x) >= 2: return x[:2] + "月"
            return "不明"
        df['月'] = df['日付'].apply(get_month)
        monthly = df.groupby('月', sort=False)['収支'].sum()
        st.bar_chart(monthly)

    with col_right:
        st.write("### 📈 機種別分析")
        summary = df.groupby('機種名').agg(平均=('収支', 'mean'), 回数=('収支', 'count'))
        summary['平均'] = summary['平均'].astype(int)
        st.table(summary)

    # --- 履歴管理（削除ボタン付き） ---
    st.divider()
    st.write("### 📝 履歴の管理")
    
    # 最新のデータが上にくるように逆順で表示
    for i, row in df.iloc[::-1].iterrows():
        c1, c2, c3, c4 = st.columns([1, 2, 1, 1])
        c1.write(row['日付'])
        c2.write(row['機種名'])
        c3.write(f"{row['収支']}円")
        if c4.button("削除", key=f"del_{i}"):
            df = df.drop(i)
            df.to_csv(FILENAME, index=False, encoding='utf-8-sig')
            st.rerun()
else:
    st.info("データがありません。")