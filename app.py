import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

st.set_page_config(page_title="多業種データジェネレーター", layout="wide")

# --- UIデザイン（文字色を濃く、枠線をはっきりさせる） ---
st.markdown("""
    <style>
    /* メトリック全体のスタイル */
    [data-testid="stMetric"] {
        background-color: #ffffff; 
        border: 2px solid #d0d0d0; /* 枠線を少し太く */
        padding: 20px !important;
        border-radius: 12px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); 
        min-height: 140px;
    }
    /* ラベル（項目名）の文字色を濃く */
    [data-testid="stMetricLabel"] {
        color: #1a1a1a !important;
        font-weight: bold !important;
        font-size: 1.1rem !important;
    }
    /* 数値の文字色を濃く */
    [data-testid="stMetricValue"] {
        color: #000000 !important;
        font-weight: 800 !important;
    }
    .main { background-color: #f9f9f9; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 次世代型・多業種ダミーデータ生成ツール")

# --- サイドバー ---
with st.sidebar:
    st.header("⚙️ 設定")
    category = st.selectbox("カテゴリーを選択", 
        ["カフェ", "居酒屋", "アパレル", "コンビニ", "ガソリンスタンド", "スーパー", "ショッピングモール", "ファミレス", "ホテル"])
    years = st.slider("期間（過去何年分か）", 1, 5, 2)
    
    # 件数指定機能の追加
    max_rows = st.number_input("表示・保存する最大件数", min_value=1, max_value=2000, value=365)
    
    st.divider()
    st.write("Ver.4.1: 表示件数指定・視認性向上モデル")

# --- 業界別詳細設定 ---
configs = {
    "カフェ": {"cust": 80, "spend": 850, "week": [1,1,1,1,1,1.5,1.3], "season": {12:1.2, 8:1.1}},
    "居酒屋": {"cust": 40, "spend": 4500, "week": [0.7,0.8,0.9,1.1,2.2,2.5,0.5], "season": {12:2.5, 3:1.5}},
    "アパレル": {"cust": 50, "spend": 12000, "week": [0.8,0.8,0.8,0.8,1.2,2.5,2.0], "season": {1:1.8, 7:1.5}},
    "コンビニ": {"cust": 800, "spend": 650, "week": [1,1,1,1,1.1,1.2,1], "season": {8:1.2}},
    "ガソリンスタンド": {"cust": 150, "spend": 5500, "week": [0.9,0.9,0.9,1,1.1,1.5,1.4], "season": {5:1.3, 8:1.4}},
    "スーパー": {"cust": 1200, "spend": 2800, "week": [1,0.9,1,0.9,1.1,1.6,1.8], "season": {12:1.5}},
    "ショッピングモール": {"cust": 5000, "spend": 5500, "week": [0.7,0.7,0.7,0.7,1.0,3.0,2.5], "season": {1:1.5, 8:1.5}},
    "ファミレス": {"cust": 200, "spend": 1400, "week": [0.8,0.8,0.9,0.9,1.2,1.8,2.0], "season": {8:1.3, 12:1.2}},
    "ホテル": {"cust": 100, "spend": 18000, "week": [0.6,0.5,0.6,0.7,1.2,2.2,0.8], "season": {5:2.0, 8:2.5, 12:1.8}}
}

conf = configs[category]

# --- データ生成 ---
today = datetime.now()
start_date = datetime(today.year - (years - 1), 1, 1)
dates = pd.date_range(start=start_date, end=today)

data = []
for date_val in dates:
    weekday, month = date_val.weekday(), date_val.month
    weather = np.random.choice(["☀️ 晴れ", "☁️ 曇り", "☔ 雨"], p=[0.6, 0.3, 0.1])
    
    event_label = "通常営業"
    event_effect = 1.0
    dice = np.random.random()
    if dice < 0.03: 
        event_label = "🎉 SNSバズり・メディア露出"
        event_effect = np.random.uniform(1.8, 3.0)
    elif dice < 0.05:
        event_label = "⚠️ 周辺競合セール・近隣工事"
        event_effect = np.random.uniform(0.5, 0.7)
    elif "☔" in weather and dice < 0.2:
        event_label = "❄️ 悪天候による客足ダウン"
        event_effect = 0.6

    cust = int(conf["cust"] * conf["week"][weekday] * conf["season"].get(month, 1.0) * event_effect * np.random.uniform(0.9, 1.1))
    spend = int(conf["spend"] * np.random.uniform(0.95, 1.05))
    
    data.append({
        "日付": date_val.date(), "イベント内容": event_label, "天候": weather, 
        "客数": cust, "客単価": spend, "売上": cust * spend
    })

# DataFrame作成
df = pd.DataFrame(data)

# 指定された件数で切り出し
df = df.tail(max_rows)

df['日付'] = pd.to_datetime(df['日付'])
df['前年日付'] = df['日付'] - pd.DateOffset(years=1)
df_prev = df[['日付', '客数', '売上']].rename(columns={'日付': '前年日付', '客数': '前年客数', '売上': '前年売上'})
df = pd.merge(df, df_prev, on='前年日付', how='left')
df['売上YoY(%)'] = ((df['売上'] / df['前年売上']) * 100).round(1)

# --- UI表示 ---
latest = df.iloc[-1]
m1, m2, m3 = st.columns(3) # カラム数を3に変更
with m1: st.metric("昨日の売上", f"¥{int(latest['売上']):,}", f"{latest['売上YoY(%)']}%")
with m2: st.metric("昨日の客数", f"{int(latest['客数'])}名")
with m3: st.metric("イベント発生総数", f"{len(df[df['イベント内容'] != '通常営業'])}件")

st.divider()
c1, c2 = st.columns([1, 1])
with c1:
    st.subheader("📈 売上推移グラフ")
    st.line_chart(df.set_index("日付")[["売上"]])
with c2:
    st.subheader("📋 履歴データ（異常値が確認できます）")
    st.dataframe(df.drop(columns=['前年日付','前年客数','前年売上']).sort_values("日付", ascending=False).fillna("-"), use_container_width=True)

csv = df.to_csv(index=False).encode('utf-8')
st.download_button(f"📩 {category}のデータを保存", csv, f"dummy_{category}.csv", "text/csv", use_container_width=True)
