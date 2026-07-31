// dataStore.js — 清福技術考稽核系統的資料存取層。
//
// 純 JavaScript，不依賴 React，供 index.html 以 <script type="module"> 載入，
// 同時也是 Vitest 測試的對象（唯一的測試接縫）。fetch / storage / 使用者身分
// 一律以參數注入，測試時替換成假物件，不接觸真實網路或真實瀏覽器。
//
// 核心設計見 docs/specs/dataStore-儲存讀取可靠性.md 第 2、3、4 節：
//   1. 所有操作回傳 Result，不拋例外、不吞錯誤。
//   2. 雲端快照（snapshot）與本機草稿（pending）是兩份不相交的資料。
//      snapshot 只在成功讀取雲端後整份覆寫，純唯讀；
//      pending 只在使用者建立紀錄且雲端寫入失敗時才產生一筆。
//      沒有任何自動把 pending 或舊快取推回雲端的機制。
//   3. 本機儲存的讀寫全部包上錯誤處理，絕不因為快取壞掉而拋出例外。

/** @typedef {{ ok: true, data: any }} Ok */
/** @typedef {{ ok: false, error: { kind: string, message: string, status?: number } }} Err */

const ERROR_KINDS = /** @type {const} */ ([
  'network', 'auth', 'forbidden', 'rejected', 'conflict', 'cache-full', 'cache-corrupt'
])

function ok(data) {
  return { ok: true, data }
}

function err(kind, message, status) {
  if (!ERROR_KINDS.includes(kind)) {
    throw new Error(`dataStore: unknown error kind "${kind}"`)
  }
  const error = { kind, message }
  if (status !== undefined) error.status = status
  return { ok: false, error }
}

// ── 本機快取：所有存取都經過這裡，絕不直接呼叫 storage.getItem/setItem ──

function cacheKey(userId, name) {
  return `ds_v1:${userId || 'anon'}:${name}`
}

function safeRead(storage, key) {
  let raw
  try {
    raw = storage.getItem(key)
  } catch (e) {
    return err('cache-corrupt', `讀取快取失敗（${key}）：${e.message}`)
  }
  if (raw == null) return ok(null)
  try {
    return ok(JSON.parse(raw))
  } catch (e) {
    return err('cache-corrupt', `快取內容損毀（${key}）：${e.message}`)
  }
}

function safeWrite(storage, key, value) {
  try {
    storage.setItem(key, JSON.stringify(value))
    return ok(undefined)
  } catch (e) {
    return err('cache-full', `寫入快取失敗（${key}）：${e.message}`)
  }
}

function safeRemove(storage, key) {
  try {
    storage.removeItem(key)
    return ok(undefined)
  } catch (e) {
    return err('cache-full', `清除快取失敗（${key}）：${e.message}`)
  }
}

// ── HTTP：統一的請求與錯誤分類 ──

async function request(fetchFn, url, options) {
  let response
  try {
    response = await fetchFn(url, options)
  } catch (e) {
    return err('network', `連線失敗：${e.message}`)
  }

  if (response.status === 401) {
    return err('auth', '未登入或憑證已失效', 401)
  }
  if (response.status === 403) {
    return err('forbidden', '權限不足，已被後端拒絕', 403)
  }
  if (response.status === 409) {
    let bodyText = ''
    try { bodyText = await response.text() } catch (_e) { /* ignore */ }
    return err('conflict', bodyText || '資料衝突（可能已存在相同紀錄）', 409)
  }
  if (response.status >= 500) {
    return err('network', `伺服器暫時性錯誤（${response.status}）`, response.status)
  }
  if (!response.ok) {
    let bodyText = ''
    try { bodyText = await response.text() } catch (_e) { /* ignore */ }
    return err('rejected', bodyText || `請求被拒絕（${response.status}）`, response.status)
  }

  if (response.status === 204) return ok(null)
  const text = await response.text()
  if (!text) return ok(null)
  try {
    return ok(JSON.parse(text))
  } catch (e) {
    return err('rejected', `回應內容非合法 JSON：${e.message}`)
  }
}

function buildHeaders(supabaseKey, token, extra) {
  return Object.assign(
    {
      apikey: supabaseKey,
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    extra || {}
  )
}

// ── 紀錄（audit_records）與人員（audit_personnel）的欄位轉換 ──
// 雲端 audit_content 是 JSONB，前端內部用扁平物件操作；轉換集中於此，
// 避免轉換邏輯散落在多個呼叫點（目前 index.html 有多處各自重複此轉換）。

function recordToPayload(rec, userId) {
  return {
    audit_content: {
      date: rec.date,
      templateId: rec.templateId || null,
      auditName: rec.auditName,
      unitCategory: rec.unitCategory || '',
      unit: String(rec.unit || '').trim(),
      target: rec.target || '',
      jobTitle: rec.jobTitle || '',
      auditor: rec.auditor || '',
      score: rec.score,
      score2: rec.score2 || null,
      notes: rec.notes || '',
      isDual: !!rec.isDual,
      technique: rec.technique || '',
      checklist: rec.checklist || []
    },
    user_id: userId
  }
}

function payloadToRecord(row) {
  const d = typeof row.audit_content === 'string' ? JSON.parse(row.audit_content) : (row.audit_content || {})
  return {
    id: row.id,
    date: d.date || (row.created_at || '').split('T')[0],
    templateId: d.templateId || null,
    auditName: d.auditName || '',
    unitCategory: d.unitCategory || '',
    unit: String(d.unit || '').trim(),
    target: d.target || '',
    jobTitle: d.jobTitle || '',
    auditor: d.auditor || '',
    score: d.score,
    score2: d.score2,
    notes: d.notes || '',
    isDual: !!d.isDual,
    technique: d.technique || '',
    checklist: d.checklist || []
  }
}

const RECORD_PAGE_SIZE = 1000
const RECORD_MAX_PAGES = 100 // 安全上限，避免分頁邏輯有誤時無限迴圈

// ── 主體 ──

/**
 * @param {object} opts
 * @param {typeof fetch} opts.fetch
 * @param {{getItem: Function, setItem: Function, removeItem: Function}} opts.storage
 * @param {string} opts.supabaseUrl
 * @param {string} opts.supabaseKey  瀏覽器可安全公開的 publishable key（不是 secret key）
 * @param {() => (string|null)} opts.getAccessToken  取得目前登入者的 access token
 * @param {() => (string|null)} opts.getUserId
 */
export function createDataStore(opts) {
  const { fetch: fetchFn, storage, supabaseUrl, supabaseKey, getAccessToken, getUserId } = opts

  function authHeaders(extra) {
    const token = getAccessToken ? getAccessToken() : null
    if (!token) return null
    return buildHeaders(supabaseKey, token, extra)
  }

  function requireAuth() {
    return err('auth', '尚未登入，無法執行此操作')
  }

  // ---- 快取鍵 ----
  const keys = {
    recordsSnapshot: () => cacheKey(getUserId(), 'records:snapshot'),
    recordsPending: () => cacheKey(getUserId(), 'records:pending'),
    personnelSnapshot: () => cacheKey(getUserId(), 'personnel:snapshot')
  }

  // ================= 紀錄 =================

  const records = {
    /** 從雲端分頁讀取全部紀錄，成功後整份覆寫本機快照。失敗時快照維持原狀。 */
    async loadSnapshot(extraQuery) {
      const headers = authHeaders()
      if (!headers) return requireAuth()

      let all = []
      for (let page = 0; page < RECORD_MAX_PAGES; page++) {
        const offset = page * RECORD_PAGE_SIZE
        const q = extraQuery ? `&${extraQuery}` : ''
        const url = `${supabaseUrl}/rest/v1/audit_records?select=*&order=created_at.desc&limit=${RECORD_PAGE_SIZE}&offset=${offset}${q}`
        const result = await request(fetchFn, url, { headers })
        if (!result.ok) return result
        const batch = (result.data || []).map(payloadToRecord)
        all = all.concat(batch)
        if (batch.length < RECORD_PAGE_SIZE) break
      }

      const writeResult = safeWrite(storage, keys.recordsSnapshot(), all)
      if (!writeResult.ok) {
        // 快取寫不進去不代表這次讀取失敗，仍把資料回傳給呼叫端顯示，
        // 只是下次離線時可能讀不到這一份最新結果。
        return ok(all)
      }
      return ok(all)
    },

    /**
     * 批次匯入多筆紀錄（例如還原備份、匯入歷史資料）。固定分批送出，
     * 每批各自成功或失敗，回傳每批的 Result 陣列，讓呼叫端能明確知道
     * 「成功幾批、哪幾批失敗」，而不是一次巨量請求要嘛全部成功要嘛全部
     * 失敗、且失敗時無法得知已經寫進去多少。
     */
    async createMany(recs, batchSize) {
      const size = batchSize || 100
      const userId = getUserId()
      const headers = authHeaders({ Prefer: 'return=minimal' })
      if (!headers) return [requireAuth()]

      const results = []
      for (let i = 0; i < recs.length; i += size) {
        const chunk = recs.slice(i, i + size)
        const payload = chunk.map(r => recordToPayload(r, userId))
        const result = await request(fetchFn, `${supabaseUrl}/rest/v1/audit_records`, {
          method: 'POST',
          headers,
          body: JSON.stringify(payload)
        })
        results.push(result)
      }
      return results
    },

    /** 讀取本機快照（唯讀，供離線顯示）。不觸發任何網路請求。 */
    getCachedSnapshot() {
      const result = safeRead(storage, keys.recordsSnapshot())
      if (!result.ok) return result
      return ok(result.data || [])
    },

    /** 讀取尚未同步的本機草稿。 */
    listPending() {
      const result = safeRead(storage, keys.recordsPending())
      if (!result.ok) return result
      return ok(result.data || [])
    },

    /**
     * 建立一筆紀錄。成功寫入雲端則直接回傳雲端資料（含真實 id）。
     * 雲端寫入失敗時，改存成本機草稿（不會拋棄），並回傳失敗結果；
     * 呼叫端應以 listPending() 取得含這筆草稿在內的最新草稿清單。
     */
    async create(rec) {
      const userId = getUserId()
      const headers = authHeaders({ Prefer: 'return=representation' })
      if (!headers) {
        // 完全離線／未登入：這不是「操作失敗」，資料沒有遺失，只是還沒同步。
        // 回傳 ok，但 data.pending=true，讓呼叫端能標示「尚未同步」而不是
        // 顯示一般的錯誤訊息。
        const stash = this._stashPending(rec)
        if (!stash.ok) return stash
        return ok({ pending: true, localId: stash.data.localId })
      }

      const url = `${supabaseUrl}/rest/v1/audit_records`
      const result = await request(fetchFn, url, {
        method: 'POST',
        headers,
        body: JSON.stringify(recordToPayload(rec, userId))
      })

      if (result.ok) {
        const row = Array.isArray(result.data) ? result.data[0] : result.data
        return ok(Object.assign({ pending: false }, payloadToRecord(row)))
      }

      const stash = this._stashPending(rec)
      // 雲端真的有嘗試寫入但失敗了（不是單純沒登入），這才是使用者該被
      // 明確告知「沒存成功」的情境，因此保留原始錯誤的 kind 往上回報，
      // 不因為本機草稿存成功就掩蓋這個失敗。額外附上 localId，讓呼叫端
      // 知道這筆已經存成草稿、可以繼續顯示在畫面上並標示未同步。
      if (!stash.ok) return stash
      result.error.localId = stash.data.localId
      return result
    },

    /** 內部方法：把一筆紀錄加進本機草稿清單，回傳它取得的本機識別碼。 */
    _stashPending(rec) {
      const listResult = safeRead(storage, keys.recordsPending())
      const list = listResult.ok ? (listResult.data || []) : []
      const localId = rec._localId || `pending_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`
      const draft = Object.assign({}, rec, { _localId: localId })
      list.push(draft)
      const writeResult = safeWrite(storage, keys.recordsPending(), list)
      if (!writeResult.ok) return writeResult
      return ok({ localId })
    },

    /** 放棄一筆本機草稿（不會、也從未送到雲端過）。純本機操作，不發送網路請求。 */
    discardPending(localId) {
      const listResult = safeRead(storage, keys.recordsPending())
      if (!listResult.ok) return listResult
      const list = (listResult.data || []).filter(r => r._localId !== localId)
      return safeWrite(storage, keys.recordsPending(), list)
    },

    /** 重新嘗試把一筆本機草稿送上雲端。成功後從草稿移除並回傳雲端資料。 */
    async retryPending(localId) {
      const listResult = safeRead(storage, keys.recordsPending())
      if (!listResult.ok) return listResult
      const list = listResult.data || []
      const draft = list.find(r => r._localId === localId)
      if (!draft) return err('rejected', '找不到這筆草稿，可能已被處理過')

      const userId = getUserId()
      const headers = authHeaders({ Prefer: 'return=representation' })
      if (!headers) return requireAuth()

      const result = await request(fetchFn, `${supabaseUrl}/rest/v1/audit_records`, {
        method: 'POST',
        headers,
        body: JSON.stringify(recordToPayload(draft, userId))
      })
      if (!result.ok) return result

      const remaining = list.filter(r => r._localId !== localId)
      safeWrite(storage, keys.recordsPending(), remaining)
      const row = Array.isArray(result.data) ? result.data[0] : result.data
      return ok(payloadToRecord(row))
    },

    /**
     * 刪除雲端上的一筆紀錄。刪除失敗時完全不動本機快照 —— 這是「刪除失敗
     * 卻從畫面上消失」問題的修法：呼叫端只依 Result.ok 決定要不要把畫面
     * 上的紀錄移除，dataStore 自己絕不提前假設會成功。
     */
    async deleteRecord(id) {
      const headers = authHeaders()
      if (!headers) return requireAuth()

      const url = `${supabaseUrl}/rest/v1/audit_records?id=eq.${encodeURIComponent(id)}`
      const result = await request(fetchFn, url, { method: 'DELETE', headers })
      if (!result.ok) return result

      const snapResult = safeRead(storage, keys.recordsSnapshot())
      if (snapResult.ok && snapResult.data) {
        const next = snapResult.data.filter(r => String(r.id) !== String(id))
        safeWrite(storage, keys.recordsSnapshot(), next)
      }
      return ok(true)
    }
  }

  // ================= 人員名單 =================

  const personnel = {
    async loadSnapshot() {
      const headers = authHeaders()
      if (!headers) return requireAuth()
      const result = await request(fetchFn, `${supabaseUrl}/rest/v1/audit_personnel?select=*`, { headers })
      if (!result.ok) return result
      safeWrite(storage, keys.personnelSnapshot(), result.data)
      return ok(result.data)
    },

    getCachedSnapshot() {
      const result = safeRead(storage, keys.personnelSnapshot())
      if (!result.ok) return result
      return ok(result.data || [])
    },

    /**
     * 新增或更新一位人員。以 (unit, category, name) 為唯一鍵 upsert，
     * 取代舊版「先刪整個機構再整批插入」——那個做法在刪除成功、插入失敗時
     * 會讓整個機構的名單消失。這裡每次只影響這一筆。
     */
    async upsert(entry) {
      const headers = authHeaders({ Prefer: 'resolution=merge-duplicates,return=representation' })
      if (!headers) return requireAuth()
      const row = { unit: String(entry.unit || '').trim(), category: entry.category, name: String(entry.name || '').trim() }
      if (!row.unit || !row.category || !row.name) {
        return err('rejected', 'unit / category / name 為必填')
      }
      const url = `${supabaseUrl}/rest/v1/audit_personnel?on_conflict=unit,category,name`
      return request(fetchFn, url, { method: 'POST', headers, body: JSON.stringify([row]) })
    },

    /** 精確刪除一位人員，不影響同機構的其他人。 */
    async remove(entry) {
      const headers = authHeaders()
      if (!headers) return requireAuth()
      // PostgREST 篩選語法是 "欄位=eq.值"；用 URLSearchParams 會連 "eq." 一起
      // 編碼掉，所以手動組字串、只對值做 encodeURIComponent。
      const qs = ['unit', 'category', 'name']
        .map(k => `${k}=eq.${encodeURIComponent(entry[k])}`)
        .join('&')
      const url = `${supabaseUrl}/rest/v1/audit_personnel?${qs}`
      return request(fetchFn, url, { method: 'DELETE', headers })
    }
  }

  // ================= 使用者切換 =================

  /** 登出或換人登入時呼叫，清除該使用者命名空間下的全部快取。 */
  function clearUserCache(userId) {
    safeRemove(storage, cacheKey(userId, 'records:snapshot'))
    safeRemove(storage, cacheKey(userId, 'records:pending'))
    safeRemove(storage, cacheKey(userId, 'personnel:snapshot'))
    return ok(undefined)
  }

  return { records, personnel, clearUserCache }
}

if (typeof window !== 'undefined') {
  window.createDataStore = createDataStore
}
