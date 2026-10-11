"""Neil Financial Desk personal research dashboard. Deploy separately on Streamlit Cloud."""
from __future__ import annotations

from pathlib import Path
import json

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "history.json"
LABELS = {
    **{"UST_" + t: "U.S. Treasury " + t for t in ("1M","2M","3M","6M","1Y","2Y","3Y","5Y","7Y","10Y","20Y","30Y")},
    "ECB_EURUSD": "ECB EUR/USD reference",
    "ECB_USDJPY": "ECB USD/JPY derived cross",
    "ECB_USDCNY": "ECB USD/CNY derived cross",
}

st.set_page_config(page_title="Neil｜Market Research Lab",page_icon="📊",layout="wide")
st.title("📊 Neil｜Market Research Lab")
st.caption("Official U.S. Treasury yields & ECB references. Not real-time; no Yahoo data redistribution.")
if not DATA.exists():
    st.info("尚未取得官方歷史資料，請先等待 GitHub Actions 更新。")
    st.stop()
try:
    store = json.loads(DATA.read_text(encoding="utf-8")).get("series",{})
except (ValueError,OSError) as e:
    st.error(f"無法讀取市場資料：{e}")
    st.stop()
valid = {k:v for k,v in store.items() if isinstance(v,list) and v and k in LABELS}
if not valid:
    st.info("資料庫尚無有效觀測值")
    st.stop()
st.sidebar.header("研究篩選")
key = st.sidebar.selectbox("指標",list(valid),format_func=lambda x: LABELS[x],index=list(valid).index("UST_10Y") if "UST_10Y" in valid else 0)
history = pd.DataFrame(valid[key])
history["date"] = pd.to_datetime(history["date"],errors="coerce")
history["value"] = pd.to_numeric(history["value"],errors="coerce")
history = history.dropna(subset=["date","value"]).sort_values("date")
history = history.drop_duplicates(subset=["date"],keep="last")
count = st.sidebar.slider("顯示最近幾筆", min_value=10,max_value=max(10,len(history)),value=min(180,max(10,len(history))),step=10)
selected = history.tail(count)
if selected.empty:
    st.warning("選擇區間沒有資料")
    st.stop()
a,b,c=st.columns(3)
last=selected.iloc[-1]
a.metric("最近觀測值",f"{last['value']:.4f}"+("%" if key.startswith("UST_") else ""))
b.metric("最近觀測日",last["date"].strftime("%Y/%m/%d"))
c.metric("觀測值筆數",str(len(history)))
chart=px.line(selected,x="date",y="value",markers=True,labels={"date":"觀測日","value":"殖利率 (%)" if key.startswith("UST_") else "參考匯率"},title=LABELS[key])
chart.update_layout(hovermode="x unified",height=470)
st.plotly_chart(chart,use_container_width=True)
with st.expander("完整數據與 CSV 下載"):
    data=selected.copy()
    data["date"]=data["date"].dt.strftime("%Y-%m-%d")
    st.dataframe(data,use_container_width=True,hide_index=True)
    st.download_button("下載觀測資料 CSV",data.to_csv(index=False).encode("utf-8-sig"),file_name=f"neil-{key}.csv",mime="text/csv")
st.info("此介面使用原本 GitHub 專案內的官方資料。美債殖利率來自 U.S. Treasury；ECB 外匯交叉換算不是 USD/TWD 台北收盤價，也不是即時 USD/CNH。")
st.caption("📝 Neil 整理｜僅供個人學習與研究，非投資建議。請勿上傳銀行內部資料或客戶個資。")
