import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 設定 ---
FILENAME = 'shuushi_data.csv'
SLOT_TANKA = 5.5  # 5.5円スロット

# データの読み込み関数
def load_data():
    if os.path.exists(FILENAME):
        try:
            df = pd.read_csv(FILENAME, encoding='utf-8-sig')
        except:
            df = pd.read_csv(FILENAME, encoding='shift-jis')
        
        # 日付を強制的に文字列にし、空欄を埋める
        df['日付'] = df['日付'].fillna('').astype(str)
        return df
    return pd.DataFrame(columns=['日付', '機種名', '投資', '回収枚数', '収支'])

# 画面設定
st.set_page_config(page_title="5.5スロ収支", layout="wide")

# --- サイドバー：確率計算機 ---
with st.sidebar:
    st.header("🎰 確率計算機")
    kaiten = st.number_input("総回転数", min_value=1, value=1000, step=100)
    big = st.number_input("BIG回数", min_value=0, value=0, step=1)
    reg = st.number_input("REG回数", min_value=0, value=0, step=1)
    
    st.divider()
    if big > 0: st.write(f"BIG確率: **1/{kaiten/big:.1f}**")
    if reg > 0: st.write(f"REG確率: **1/{kaiten/reg:.1f}**")
    if (big + reg) > 0: st.info(f"合成確率: **1/{kaiten/(big+reg):.1f}**")

# --- メイン画面 ---
st.title("🎰 5.5スロ収支表")

# 📝 記録フォーム
with st.form("input_form", clear_on_submit=True):
    st.write("### 稼働を記録")
    col1, col2 = st.columns(2)
    with col1: date = st.date_input("日付", datetime.now())
    with col2: name = st.text_input("機種名")
    
    col3, col4 = st.columns(2)
    with col3: toushi = st.number_input("投資(円)", min_value=0, step=500)
    with col4: maisuu = st.number_input("回収(枚)", min_value=0, step=10)
    
    if st.form_submit_button("記録する"):
        df = load_data()
        shuushi = int(maisuu * SLOT_TANKA) - toushi
        new_row = pd.DataFrame([[date.strftime("%m/%d"), name, toushi, maisuu, shuushi]], 
                               columns=['日付', '機種名', '投資', '回収枚数', '収支'])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(FILENAME, index=False, encoding='utf-8-sig')
        st.success(f"記録完了！ 収支: {shuushi}円")
        st.rerun()

# --- データ表示・分析 ---
df = load_data()

if not df.empty:
    st.divider()
    st.metric("累計トータル収支", f"{df['収支'].sum()} 円")

    col_left, col_right = st.columns(2)
    with col_left:
        st.write("### 📅 月別収支")
        # 月抽出の修正：リストの0番目（月）を取り出して「月」を足す
        def get_month(x):
            if '/' in x:
                return x.split('/')[0] + "月"
            if len(x) >= 2:
                return x[:2] + "月"
            return "不明"
        
        df['月'] = df['日付'].apply(get_month)
        monthly = df.groupby('月', sort=False)['収支'].sum()
        st.bar_chart(monthly)

    with col_right:
        st.write("### 📈 機種別分析")
        summary = df.groupby('機種名').agg(平均=('収支', 'mean'), 回数=('収支', 'count'))
        summary['平均'] = summary['平均'].astype(int)
        st.table(summary)

    # --- 修正・削除機能 ---
    st.write("### 📝 履歴の管理（修正・削除）")
    st.info("表の数字を直接書き換えるか、行を選んで削除（Deleteキー）できます。最後に保存ボタンを押してください。")
    
    # 編集用の一時的なデータ（月列なし）
    df_for_edit = df.drop(columns=['月']) if '月' in df.columns else df

    edited_df = st.data_editor(
        df_for_edit,
        num_rows="dynamic",
        use_container_width=True,
        column_config={"収支": st.column_config.NumberColumn(format="%d 円")},
        key="data_editor"
    )

    if st.button("履歴の変更を保存する"):
        edited_df.to_csv(FILENAME, index=False, encoding='utf-8-sig')
        st.success("保存しました！")
        st.rerun()
else:
    st.info("データがまだありません。")