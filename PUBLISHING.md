# Neil Financial Desk｜ChatGPT 一鍵發布 SOP v1
最後更新：2026-10-11｜GitHub: `hsliu66-ctrl/neil-finance`｜網站: https://hsliu66-ctrl.github.io/neil-finance/

## 目的與限制
這是「在 ChatGPT 下達一次明確的發布命令 → ChatGPT 透過**已授權 GitHub 連接**更新報告 → GitHub Pages 自動部署」的工作流程。不需要在 iPad 的 GitHub 網頁手動上傳。它**不是** GitHub Pages 前端直接寫 GitHub，也不是背景定時自動發布；需要當次對話具備 GitHub 工具權限，且使用者明確傳送「正式發布」指令。使用者沒有提供文章內容或檔案時，只能啟動流程，不能捏造內容。

## 在 ChatGPT 使用
1. 貼上、上傳、或在同一對話先提供報告原始資料（新聞、行情、PDF、本人整理分析）。
2. 傳送「**發布 Neil 財經報告**」或「**把以上資料正式發布至 Neil Financial Desk**」。該當次訊息就是公開發布授權；「僅預覽／草稿」則不寫入 GitHub。
3. ChatGPT 編輯、查核來源、完成文章資料結構，具備足夠可核對的資料且不違反隱私／著作權才將新版本推送到 `main`，並查詢 GitHub Pages 部署狀態。
4. 部署成功回覆永久文章連結、commit 與來源日期。若查核不完整、資料缺漏、權限不足或部署失敗，明確回報，**不可說已成功**。

最短指令：
```
發布 Neil 財經報告｜主題：美股投資晨報｜報告日期：2026-10-11
資料來源：[來源/網址]
正文：[貼上報告，或使用本對話已上傳附件]
請保留已確認數據、Neil 觀點、資料來源與免責聲明，直接發布到我的 GitHub Pages。
```

## 出版規格
- 語言：繁體中文；網站現有暖白、深海軍藍、墨綠／金色設計及 Neil Logo 不改動。
- 六分類 ID：`market` 美股晨報／`macro` 全球總經／`rates` 美債殖利率／`fx` 匯率週報／`etf` ETF 研究／`earnings` 財報洞察。
- 必備：`id, title, subtitle, date (YYYY-MM-DD), category, readingMinutes, summary, focus, tags, metrics, chart, sections, source, sourceUrl, sample`。依現有 `reports.js` 資料欄位維持向後相容； `sample=false` 代表完成查核後的正式報告。
- `metrics` 為物件陣列 `[{label, value, note}]`，`chart` 可為 `{label, unit, points:[{label,value}]}` 或 `null`（數據不足時不能編造走勢）；`sections` 為 `[{heading, paragraphs?:string[], bullets?:string[]}]`。
- `sourceUrl` 僅接受核實真實的 http(s) 網址；沒資料留空字串。行情要標資料日期、時區/市場、收盤或盤中、單位與來源；新聞中的預測不能當作已發生事實。
- 不修改現有文章 ID、日期及數值；若同日同類別另有報告，以明確標題／ID 區分，若使用者說「更新某篇」才修改其既有 ID。新文章按日期排序或置前皆可，頁面本身按日期顯示。
- 不冒充原作者／來源，不編造引用、交易日、圖表或數字；沒有授權不要公開 FactSet 原文、銀行內部文件、客戶／帳戶資料或其他機密內容。個人研究摘要須遵守引用授權。

## 發布時給 ChatGPT 的技術工作指引
1. 每次都從 GitHub 讀取最新 `main:reports.js`（不得使用聊天中舊副本）。解析 `window.NEIL_REPORTS = [...];`，檢查是否為陣列並保留既有所有項目。
2. 根據經確認的來源建出一篇新報告資料物件；不確定欄位不填猜測。若缺少標題、報告日期、基本來源或正文，先提出一個關鍵問題，或停止正式發布並說明缺口。
3. 以語意與 `id` 查重；新增時不得覆蓋舊文章。更新特定報告時須有使用者明確指令。不要把示範文章偷偷改成正式文章。
4. 用 GitHub `update_file` 攜帶從 `fetch_file` 取得的最新 blob `sha` 更新 `reports.js`（或建立一個原子 Git commit）。如產生衝突，重新讀取與合併，勿強制覆蓋他人的更新。
5. 查詢 `pages build and deployment` 之執行結果，確認最新 commit 顯示 `completed / success` 才能說正式上線；若仍建置中就如實告知。
6. 回報 URL：`https://hsliu66-ctrl.github.io/neil-finance/article.html?id=<URL-encoded id>`，並附來源核對摘要、報告日期、commit 連結、部署狀態。
7. 使用者說「預覽」時只製作稿件，不寫入 GitHub；使用者說「撤下」必須先判斷是否要從公開檔案移除及保留 Git 歷史（Git 歷史中的內容仍可能可見），取得明確範圍再操作。

## 常見問題
- 只要 ChatGPT 有 GitHub 連接，就**不需要**在 iPad 找「Add file」。
- 網站公開工作台 `publish.html` **不能直接操作 GitHub**；只會在本機組裝與複製發布訊息，使用者貼到 ChatGPT 後發送，才會觸發對話中的 GitHub 工具。
- GitHub Pages 不是資料庫或排程器；要定期自動抓行情、定時發布還需要額外資料管道與權限設定。
- 任何可公開的頁面皆可能被其他人讀到，不要貼入機密或個人資料。
