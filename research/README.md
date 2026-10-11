# Neil Research Lab｜研究工具安裝與使用

這個目錄整合五個 GitHub 開源專案；GitHub Pages 是靜態網站，並不能直接執行 Python、Streamlit 伺服器或 LEAN/Docker 回測。程式碼已加入 Repository，執行環境依各工具分開。

| 工具 | Repository 中的檔案 | 運行方式 |
|---|---|---|
| Plotly.py | \`research/plotly_chart.py\` | GitHub Actions 產生公開美債殖利率互動 HTML；頁面 \`research-plotly.html\` |
| yfinance | \`research/private_yfinance.py\` | **僅本機私人研究**；不得未經 Yahoo 授權將擷取的行情自動公開 |
| Streamlit | \`research/streamlit_app.py\` | 可在本機啟動，或另行透過 Streamlit Community Cloud 與 GitHub 綁定 |
| Quarto | \`research/make_quarto.py\` | GitHub Actions 建立 HTML 報告附件；不會覆蓋主站 |
| QuantConnect LEAN | \`research/lean/NeilETFStrategy/main.py\` | 僅示範策略原始碼；CLI 回測需 Docker、歷史資料及相應 QuantConnect 帳號/訂閱 |

## iPad 最簡便入口
網站「研究工具」：[https://hsliu66-ctrl.github.io/neil-finance/research-lab.html](https://hsliu66-ctrl.github.io/neil-finance/research-lab.html)

## Streamlit 獨立上線（需要由使用者授權一次）
前往 https://share.streamlit.io/ 登入並選擇 Create app，填入：
- Repository: \`hsliu66-ctrl/neil-finance\`
- Branch: \`main\`
- Entry point / Main file: \`research/streamlit_app.py\`
- Dependencies: \`research/requirements.txt\`（Streamlit Community Cloud 自動偵測）

只有 Streamlit 平台確認部署後才有真正的 \`*.streamlit.app\` 公開網址；不要捏造網址。公開 App 只讀已公開的美債和 ECB 資料。

## 在桌面或 GitHub Codespaces 啟動 Python 研究工具
\`\`\`bash
python -m pip install -r research/requirements.txt
python research/plotly_chart.py
python research/private_yfinance.py VT --period 1mo
streamlit run research/streamlit_app.py
\`\`\`

yfinance 的 Yahoo 資料只供符合其條款的個人研究；\`private_yfinance.py\` 僅輸出到本機終端，不寫入 GitHub 檔案。

## Quarto
GitHub Actions -> \`Neil Research Tools - Validate and Quarto\` -> Run workflow，會執行 \`research/make_quarto.py\` 並透過 \`quarto-dev/quarto-actions/setup@v2\` 安裝 Quarto，輸出 HTML 報告到 workflow artifacts，**不自動公開發布**。

## LEAN
\`\`\`bash
python -m pip install -r research/requirements-lean.txt
lean --version
# 依 QuantConnect 官方文件安裝 Docker、準備資料並登入符合資格的 QuantConnect 組織
lean init
lean backtest "research/lean/NeilETFStrategy"
\`\`\`

不要在 iPad 預期原生執行 Docker。LEAN CLI 的特定功能可能需要付費組織；上面只是準備操作範例，不代表已在雲端成功執行回測或提供投資建議。

## GitHub 排程
既有官方資料更新排程 **台北時間週一至週六 06:30** 保持不變。
專案添加工具不會自動新增 Yahoo Finance 資料擷取或更動市場資料的授權與公開政策。

## 來源
- https://github.com/plotly/plotly.py
- https://github.com/ranaroussi/yfinance
- https://github.com/streamlit/streamlit
- https://github.com/quarto-dev/quarto-cli
- https://github.com/QuantConnect/Lean
