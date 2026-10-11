#!/usr/bin/env python3
"""Generate a public Plotly interactive yield-curve page from verified U.S. Treasury history."""
from __future__ import annotations
import argparse
import html
import json
from pathlib import Path
import plotly.graph_objects as go

ROOT = Path(__file__).resolve().parents[1]
TENORS = [("1M",1/12),("2M",2/12),("3M",.25),("6M",.5),("1Y",1),("2Y",2),("3Y",3),("5Y",5),("7Y",7),("10Y",10),("20Y",20),("30Y",30)]

def make_page(history_file: Path, output: Path) -> int:
    history = json.loads(history_file.read_text(encoding="utf-8"))
    series = history.get("series", {})
    by_tenor = {}
    for term, _ in TENORS:
        by_tenor[term] = {row["date"]: float(row["value"]) for row in series.get("UST_"+term, [])
                          if isinstance(row.get("value"), (int, float))}
    common = set.intersection(*(set(by_tenor[t]) for t,_ in TENORS)) if all(by_tenor.values()) else set()
    if not common:
        content = "<h1>U.S. Treasury Yield Curve</h1><p>尚無完整且經核對的 12 期同日資料。</p>"
    else:
        last = sorted(common)[-1]
        prior = [d for d in sorted(common) if d < last]
        lines = []
        for label, date in [("Latest observation",last),("Previous comparable observation",prior[-1] if prior else None)]:
            if not date: continue
            lines.append(go.Scatter(
                x=[name for name,_ in TENORS],
                y=[by_tenor[name][date] for name,_ in TENORS],
                mode="lines+markers",
                line={"width":3 if date==last else 2},
                name=f"{label}: {date}",
                hovertemplate="%{x}: %{y:.3f}%<extra></extra>"
            ))
        fig = go.Figure(data=lines)
        fig.update_layout(
            title=f"U.S. Treasury Daily Par Yield Curve · {last}",
            template="plotly_white",xaxis_title="Maturity",yaxis_title="Yield (%)",
            height=590,margin=dict(l=45,r=25,t=85,b=65),
            font=dict(family="Arial, Noto Sans TC, sans-serif",size=14),
            legend=dict(orientation="h",y=-.21),
            hovermode="x unified"
        )
        content = fig.to_html(full_html=False,include_plotlyjs="cdn",config={"displaylogo":False,"responsive":True})
    page = """<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>U.S. Treasury｜Neil Financial Desk</title>
<style>body{font-family:-apple-system,BlinkMacSystemFont,"Noto Sans TC",sans-serif;background:#f7f5ee;color:#142b36;margin:0;padding:22px}.wrap{max-width:1120px;margin:auto}a{color:#285b4d}p{line-height:1.8}footer{font-size:13px;border-top:1px solid #d5d9d2;padding-top:16px;color:#50616b;margin-top:22px}</style></head><body><main class="wrap"><p><a href="index.html">← Neil 財經研究室</a> · <a href="research-lab.html">研究工具</a></p><h1>U.S. Treasury｜互動殖利率曲線</h1>
<p>Plotly.py 產生。資料來自美國財政部 Daily Treasury Par Yield Curve Rates；只取 12 期同一觀測日數值，不拼接不同日期，非即時報價。</p>""" + content + """<footer>📝 Neil 整理｜資料來源：<a href="https://home.treasury.gov/resource-center/data-chart-center/interest-rates">U.S. Treasury</a>｜僅供資訊參考，非投資建議。互動圖表載入 Plotly CDN 需網路連線。</footer></main></body></html>"""
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(page, encoding="utf-8")
    print(f"Generated {output} using {len(common)} complete historical observation dates.")
    return len(common)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data",type=Path,default=ROOT/"data/history.json")
    parser.add_argument("--output",type=Path,default=ROOT/"research-plotly.html")
    args = parser.parse_args()
    make_page(args.data,args.output)
