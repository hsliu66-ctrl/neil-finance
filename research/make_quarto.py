#!/usr/bin/env python3
"""Generate a Quarto research memo from verified, versioned official observations."""
from pathlib import Path
import argparse, datetime as dt, json

ROOT=Path(__file__).resolve().parents[1]
def build(data,out):
    payload=json.loads(data.read_text(encoding="utf-8"))
    series=payload.get("series",{})
    order=["UST_1M","UST_2M","UST_3M","UST_6M","UST_1Y","UST_2Y","UST_3Y","UST_5Y","UST_7Y","UST_10Y","UST_20Y","UST_30Y","ECB_EURUSD","ECB_USDJPY","ECB_USDCNY"]
    rows=[]
    for key in order:
        if key not in series: continue
        x=series[key]
        rows.append(f"| {key} | {x.get('date','—')} | {float(x['value']):.4f} | {x.get('source','—')} |")
    if not rows: rows=["| 尚無已驗證資料 | — | — | — |"]
    latest_date=max((x.get("date","") for x in series.values()),default="無資料")
    content="""---
title: "Neil Financial Desk｜官方市場研究簡報"
subtitle: "U.S. Treasury / ECB · Verified observations"
format:
  html:
    toc: true
    theme: cosmo
lang: zh-Hant
---

# 研究資料概要

**資料最新觀測日（依不同指標可能不一致）：** """+latest_date+"""

本報告由 Quarto 根據專案的已存檔官方資料產生，並非即時行情、交易建議或正式 FactSet 授權內容。

## 官方觀測值

| 研究指標 | 觀測日期 | 數值 | 資料來源 |
|:--|:--|--:|:--|
"""+"\n".join(rows)+"""

::: {.callout-note}
美債資料單位為年化殖利率百分比；ECB EUR/USD 為歐元參考匯率，USD/JPY、USD/CNY 為由 ECB 歐元參考價計算的交叉匯率，**不是**外匯交易所收盤價。缺漏的官方資料不補造。
:::

## 研究方法與限制

- 依來源標記各指標的**觀測日期**，不混淆資料更新日與交易收盤日。
- 此版本不含 USD/TWD 台北外匯市場收盤、USD/CNH 或美股 ETF 即時行情。
- 若要對外引用，須核對官方最新公布數據及轉載授權。

## 資料來源

- [U.S. Treasury - Interest Rates](https://home.treasury.gov/resource-center/data-chart-center/interest-rates)
- [ECB - Euro foreign exchange reference rates](https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html)

📝 Neil 整理｜僅供資訊參考，非投資建議。
"""
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(content,encoding="utf-8")
    print(f"Quarto source written to {out}")
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--data",type=Path,default=ROOT/"data/latest.json")
    p.add_argument("--output",type=Path,default=ROOT/"research/generated_brief.qmd")
    a=p.parse_args()
    build(a.data,a.output)
