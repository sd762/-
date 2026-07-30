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

## 🚀 部署與使用方式
* **Web 線上版本**：[https://sd762.github.io/-/](https://sd762.github.io/-/)
* **桌面端啟動**：執行 `python app.py` 即可開啟獨立 Chrome 應用程式視窗。
