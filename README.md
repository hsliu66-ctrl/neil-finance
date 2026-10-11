# Neil Financial Desk｜財經研究室
官網：https://hsliu66-ctrl.github.io/neil-finance/

以繁體中文呈現美股晨報、全球總經、公債殖利率、匯率週報、ETF 研究與財報洞察。

## 目前狀態
- ✅ GitHub Pages 已成功發布：`main` 分支 `/(root)`。
- ✅ 網站使用 Neil 原始 Logo、favicon、手機響應式頁面、文章搜尋與圖表。
- ✅ **ChatGPT 財經報告發布工作台**：`publish.html`（產生與複製發佈指令，並開啟 ChatGPT）。
- ✅ 使用者傳送明確「發布 Neil 財經報告」指令且已授權 GitHub 時，ChatGPT 可直接更新 `reports.js`；GitHub Pages 自動重新部署。
- ℹ️ `editor.html` 是本機前端編輯器，輸出檔案後仍需上傳；`publish.html` 本身不會直接寫 GitHub。
- ℹ️ 初始報告為示範內容，不是即時金融行情。不得公開銀行客戶資料或未授權報告原文。

## 簡單操作
在 ChatGPT 對話提供資料並傳送：
```
發布 Neil 財經報告
主題：美股投資晨報
報告日期：YYYY-MM-DD
資料來源：（請提供）
原始內容：（貼上報告或附件）
核對數據後直接發布到 Neil Financial Desk，回覆文章網址與部署狀態。
```
或在 [ChatGPT 發布工作台](https://hsliu66-ctrl.github.io/neil-finance/publish.html) 組裝指令。

## 發布規範
請閱讀 [ChatGPT 發布 SOP](PUBLISHING.md) 與 [可複製發布指令](CHATGPT_PUBLISH_PROMPT.md)。
使用者必須在當次對話明確授權公開發布；資料不足、涉及敏感資訊或授權不明時不可擅自上線。

## V2：自動市場數據與研究歸檔
- 官方市場數據儀表板：[\`market.html\`](https://hsliu66-ctrl.github.io/neil-finance/market.html)
- 每週自動歸檔：[\`archive.html\`](https://hsliu66-ctrl.github.io/neil-finance/archive.html)
- \`data/history.json\` 和 \`data/latest.json\`：持久化官方觀測序列與最新值。
- \`data/weekly-index.json\` 和 \`data/weekly/*.json\`：每週的數據摘要與已發布文章列表。
- \`scripts/update_market.py\` 與 \`.github/workflows/neil-market-pages.yml\`：定時更新、儲存與 Pages 發布。
- 正式文章可含 \`images:[{src,alt,caption}]\`；圖卡應上傳至 \`assets/reports/\`，不可引用未經授權的資料與圖片。
- **必要的一次性設定**：GitHub Settings → Pages → Source 改為 **GitHub Actions**，才能確保 Actions 排程推送的資料會自動發布。請參考 [完整 SOP](PUBLISHING.md)。
- 資料非即時行情；Treasury 官方美債殖利率與 ECB 參考匯率有觀測日、發布時差與節假日缺值。

## 市場資料更新時間（2026-10-11 調整）
- 週一至週六 **台北時間上午 06:30**；對應 UTC 前一日 **22:30**，GitHub Actions cron 為 `30 22 * * 0-5`（UTC 週日至週五）。
- 每週歸檔維持 **週一台北時間 09:30**（UTC 01:30）。
- GitHub Actions 可能延遲執行，且資料依官方觀測日期與發布時點更新，不代表每日 06:30 已取得該日收盤數字。

## Research Lab：五大開源工具
- 首頁新增 [研究工具中心](https://hsliu66-ctrl.github.io/neil-finance/research-lab.html)。
- Plotly：網站互動公債圖表 `research-plotly.html`、Python 圖表腳本 `research/plotly_chart.py`，研究環境安裝依 `research/requirements.txt`。
- yfinance：`research/private_yfinance.py`（只供個人研究，不自動對外散布）。
- Streamlit：`research/streamlit_app.py` 已準備，但必須在 Streamlit Community Cloud 另外授權及部署。
- Quarto：`research/make_quarto.py` 與 GitHub Actions 提供研究簡報 HTML artifact；不覆蓋主站。
- QuantConnect LEAN：`research/lean/NeilETFStrategy/main.py` 為季度 ETF 配置策略範例；回測前須具 Docker、資料及有效帳號。
- GitHub Actions 檢查 workflow：`.github/workflows/neil-research-tools.yml`。驗證安裝成功不等於 Streamlit 公開託管或 LEAN 完成回測。
- 原本官方市場數據排程繼續週一至週六 **台北時間 06:30**。
