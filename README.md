# 清福技術考稽核系統 (Qingfu Technical Assessment & Audit System)

## 📌 專案簡介
本系統為專屬長期照顧機構（養老院、護理之家）設計之技術考核與照護品質稽核管理系統。提供前端無編譯單頁應用 (SPA)、雙指標評核機制、自動計分、雲端資料同步、多維度統計與專業 Excel 報表匯出功能。

---

## 🛠️ 技術架構 (Tech Stack)
* **前端框架**：React 18 + Babel Standalone + Tailwind CSS（瀏覽器端直接渲染）。
* **報表處理**：`ExcelJS` / `xlsx-js-style`（生成雙頁簽專業統計與明細 Excel 報表）、`Mammoth.js`（Word 檔解析）。
* **雲端資料庫**：[Supabase](https://supabase.com) (PostgreSQL) + Supabase Auth（處理身分驗證與 `audit_records` / `audit_personnel` 資料表）。
* **本地離線快取**：`LocalStorage` 封裝快取機制（支援無網路或雲端連線延遲時的暫存）。
* **桌面端啟動器**：`app.py`（Python 自動搜尋 Chrome 並以 `--app` 視窗模式開啟網頁）。

---

## 📝 重要修復與優化紀錄 (Fix & Maintenance Log)

### 🗓️ 2026-07-30 修復紀錄：離線快取死迴圈與未來異常年份過濾修復

#### 1. 問題描述 (Issue Summary)
* **現象一（總表顯示全空白 `-`）**：當使用者誤填了未來年份紀錄（如 `2029/07/13`）並刪除該筆資料後，分析總表的年份選擇器停留在 `2029` 年。因 2029 年已無任何紀錄，導致所有月份 (1~12月) 及年平均全部顯示為 `-`。
* **現象二（刪除紀錄死灰復燃且產生重複）**：刪除雲端紀錄後，當重新整理網頁時，瀏覽器 LocalStorage 內殘留的舊快取會被前端的「離線自動遷移機制」判定為未同步草稿，自動再次 POST 傳回 Supabase 雲端，導致資料刪不掉且重複產生。

#### 2. 修復方案 (Solution & Code Changes)
* **年份選單自動重置與上限攔截** (`availableYears` & `useEffect`)：
  - `availableYears` 設定年份過濾上限為 `currentYear + 1`，防堵任何異常未來年份進入選單。
  - 新增 `useEffect` 監聽年份列表，若當前選取年份不存在或被刪除，自動切換至最新有效年份（如 `2026`）。
* **離線自動遷移防護** (`loadAllDataFromCloud` & Auto-Sync)：
  - 離線同步過濾器新增年份檢驗（`y <= currentYear + 1`），**絕對禁止** LocalStorage 殘留的未來異常年份資料再次自動推送至雲端。
* **本機快取覆寫清理** (`Storage.saveRecords`)：
  - 每次從雲端讀取最乾淨的紀錄後，自動將資料覆寫回 LocalStorage，徹底抹除瀏覽器本地殘留的無效舊快取。
* **雲端實體 ID 綁定與刪除同步** (`saveRecordToCloud` & `handleDeleteSingle`)：
  - 新增紀錄時，使用 Supabase `Prefer: return=representation` 取得雲端產生的真正實體 ID 並同步回前端 state。
  - 刪除操作時同步觸發 `Storage.saveRecords`，確保本地快取與雲端同步完成刪除。

---

### 🗓️ 2026-11-09 更新紀錄：列印版面、依月份帶出項目、取消勾選與 Excel 匯出修復

#### 1. 匯出 Excel 的 Logo／A4 版面「從來沒有生效」的根因（重要）
* **現象**：匯出報表沒有機構 Logo，且需要每次手動調整頁面才能列印。
* **根因 A**：`addLogoToWorkbook` 以 `uint8Array.buffer` 載入，但 `XLSX.write(type:'array')` 回傳的是 **ArrayBuffer**（沒有 `.buffer`），結果載入 `undefined` → 一律拋錯 → 被 `catch` 吞掉 → 退回「無 Logo、無版面設定」的原始檔。已改為相容 ArrayBuffer / Uint8Array。
* **根因 B（修好 A 之後才會暴露）**：SheetJS 產生的檔案沒有 `<sheetFormatPr>`，ExcelJS 載入再寫出時會漏掉**必填屬性 `defaultRowHeight`**，Excel 會判定檔案毀損而打不開。已在載入後逐一補上 `defaultRowHeight = 15`。
* **教訓**：此類問題不能只靠閱讀程式碼或確認函式存在，必須**實際產出檔案並用 Excel 開啟驗證**。失敗時現在會跳出提醒，不再靜默退回。

#### 2. 列印版面（A4 一鍵可印）
* 技術考（非洗手）匯出改成比照紙本評核表：**查核項目在列、受測人員在欄、每頁 10 人**，鎖 **A4 直向**；欄寬、列高依項目數與文字長度自動計算，**項目少會撐滿、項目多自動縮成單頁**。日期列改為「月/日」避免折行。
* **超過 10 人不另開分頁**：同一張工作表，第 11 位起以區塊往右延伸；每個區塊自帶標題與「查核項目／配分」欄與 Logo，並以**多重列印範圍**讓一個區塊印成一頁（一次列印、雙面列印皆可）。因 Excel 在「縮成 N 頁」模式會忽略手動分頁，改為自行計算固定縮放比例。
* **多重列印範圍的坑**：ExcelJS 的 pageSetup.printArea 以 && 分隔多個範圍時，會寫成多個重複的 _xlnm.Print_Area 定義，Excel 只認最後一個。所以改為匯出後用 **JSZip（jszip@3.10.1，已鎖版本）** 直接把單一定義（範圍以逗號分隔）寫進 xl/workbook.xml。
* 洗手稽核明細：維持原計分與欄位，鎖 A4 直向，**每 3 人強制一頁**；統計報表為 A4 橫向。
* 分析總表：A4 橫向縮成一頁寬，並補上原本缺少的欄寬（實測 15 頁 → 3 頁）。

#### 3. 先選日期 → 自動帶出當月表定項目
* 現場考評改為先選「考核日期」，項目清單只列當月表定項目（取得方式與分析報表一致：年度覆寫 → 後台統一設定 → 預設）。可勾選「顯示全部項目（補考／加考）」。
* 項目名稱標註適用對象 **(護理)／(照服)／(護理照服)**（僅顯示用，不改儲存的 `auditName`）。判斷時注意 `AN(` 含有 `N(`，護理縮寫需排除前面是英文字母的情況。

#### 4. 紀錄庫：避免忘記取消上一家的勾選
* 新增「✕ 取消全部勾選」按鈕；勾選跨多個機構或含不在目前畫面的舊勾選時，顯示橘色警示，並在匯出前跳確認視窗列出涉及機構。
* 刻意**不採用「匯出後自動取消」**：常見流程是先匯出備份再批次刪除同一批，自動取消會讓使用者刪不到。

#### 5. 同步
* 合併 GitHub 上的登入錯誤訊息修正（9/4，依錯誤類型顯示原因並 trim email 空白）。

> **驗證方式（日後修改匯出功能時請重做）**：用 `@babel/parser` 從 `index.html` 抽出真正的 `addLogoToWorkbook` / `doExportExcel`，餵入擬真資料產出 xlsx，再以 Excel COM 開檔、量測紙張／方向／縮放並 `ExportAsFixedFormat` 匯出 PDF 數頁數。

---

## 🚀 部署與使用方式
* **Web 線上版本**：[https://sd762.github.io/-/](https://sd762.github.io/-/)
* **桌面端啟動**：執行 `python app.py` 即可開啟獨立 Chrome 應用程式視窗。

---

## 🔄 開發部署流程 (Deployment Workflow)

> **原則：先在地端測試站驗證，確認無誤後再同步正式站**，避免測試期間影響線上使用者。

### ⚠️ 必須同步的檔案（缺一不可）
本專案自 2026-08 起將資料存取層拆分為獨立檔案，**每次同步都必須複製以下兩個檔案**：

| 檔案 | 說明 |
|---|---|
| `index.html` | 主程式（React SPA） |
| `dataStore.js` | 資料存取層（以 `<script>` 載入） |

> 若只複製 `index.html` 而漏掉 `dataStore.js`，頁面會出現 `TypeError: window.createDataStore is not a function` 並完全無法開啟。

### 步驟

**1. 修改主檔**
編輯專案根目錄的 `index.html`（必要時一併修改 `dataStore.js`）。

**2. 同步到地端測試站並驗證**
```powershell
Copy-Item index.html test_local\index.html -Force
Copy-Item dataStore.js test_local\dataStore.js -Force
```
啟動本機伺服器（於專案根目錄執行）：
```bash
python -m http.server 8800
```
瀏覽器開啟 `http://localhost:8800/test_local/index.html`，確認：
* 頁面正常渲染（登入畫面出現、無紅色錯誤橫幅）
* 開發者工具 Console 無錯誤
* 本次修改的功能運作正常

**3. 同步到正式站並推送**
```powershell
Copy-Item index.html temp_git_repo\-\index.html -Force
Copy-Item dataStore.js temp_git_repo\-\dataStore.js -Force
```
```bash
cd temp_git_repo/-
git add index.html dataStore.js
git commit -m "說明本次變更"
git push origin main
```

**4. 確認上線**
GitHub Pages（repo：`https://github.com/sd762/-.git`）約 1~2 分鐘後自動部署完成。
使用者需按 **Ctrl+Shift+R** 強制重新整理以避開瀏覽器快取。

### 檔案一致性檢查
三處版本應完全相同，可用雜湊值快速比對：
```powershell
Get-FileHash index.html, test_local\index.html, temp_git_repo\-\index.html -Algorithm MD5 |
    Format-Table Path, Hash -AutoSize
```
