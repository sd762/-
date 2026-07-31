// dataStore.test.js — 覆蓋 spec 第 18 個必測情境。
//
// 只驗證外部可觀察的行為：給定輸入與外部回應，dataStore 回傳什麼結果、
// 對外送出了什麼請求、本機儲存變成什麼狀態。不斷言內部實作細節。

import { describe, it, expect, beforeEach } from 'vitest'
import { createDataStore } from './dataStore.js'

const SUPABASE_URL = 'https://example.supabase.co'
const SUPABASE_KEY = 'anon-key-for-test'

// ── 假 storage：記憶體實作，可設定為容量爆掉或內容損毀 ──

function createFakeStorage() {
  const map = new Map()
  let failOnSet = false
  return {
    getItem: (key) => (map.has(key) ? map.get(key) : null),
    setItem: (key, value) => {
      if (failOnSet) throw new Error('QuotaExceededError（模擬容量爆掉）')
      map.set(key, value)
    },
    removeItem: (key) => { map.delete(key) },
    _raw: map,
    _setFailOnSet: (v) => { failOnSet = v },
    _corrupt: (key) => { map.set(key, '{this is not valid json') }
  }
}

// ── 假 fetch：依腳本依序回應，並記錄每次實際送出的請求 ──

function createFakeFetch(script) {
  const calls = []
  let i = 0
  const fn = async (url, options) => {
    calls.push({ url, method: (options && options.method) || 'GET', headers: (options && options.headers) || {}, body: options && options.body })
    if (i >= script.length) throw new Error('fake fetch: 腳本用完了，還有未預期的請求')
    const next = script[i]
    i++
    if (typeof next === 'function') return next()
    if (next.throws) throw next.throws
    return {
      ok: next.status >= 200 && next.status < 300,
      status: next.status,
      text: async () => (next.body === undefined ? '' : JSON.stringify(next.body))
    }
  }
  fn.calls = calls
  return fn
}

function makeStore({ fetch, storage, userId }) {
  return createDataStore({
    fetch,
    storage: storage || createFakeStorage(),
    supabaseUrl: SUPABASE_URL,
    supabaseKey: SUPABASE_KEY,
    getAccessToken: () => 'user-token-123',
    getUserId: () => (userId === undefined ? 'user-1' : userId)
  })
}

const sampleRecord = () => ({
  date: '2026-07-31', auditName: '洗手遵從性', unit: '清福一館', target: '王小明',
  jobTitle: '護理師', auditor: '主管A', score: 90, checklist: []
})

describe('1. 建立紀錄，雲端回應失敗', () => {
  it('回傳失敗結果、進入草稿區、快照不受影響', async () => {
    const storage = createFakeStorage()
    // 先放一份既有快照，確認建立失敗時它完全沒被動到
    storage.setItem('ds_v1:user-1:records:snapshot', JSON.stringify([{ id: 'old-1' }]))

    const fetch = createFakeFetch([{ status: 500 }])
    const store = makeStore({ fetch, storage })

    const result = await store.records.create(sampleRecord())
    expect(result.ok).toBe(false)
    expect(result.error.kind).toBe('network')

    const pending = store.records.listPending()
    expect(pending.ok).toBe(true)
    expect(pending.data).toHaveLength(1)
    expect(pending.data[0].target).toBe('王小明')
    // 失敗結果要附上這筆草稿的本機 id，呼叫端才知道可以繼續在畫面上
    // 顯示這筆「未同步」的紀錄，而不是當它完全遺失。
    expect(result.error.localId).toBe(pending.data[0]._localId)

    const snapshot = store.records.getCachedSnapshot()
    expect(snapshot.data).toEqual([{ id: 'old-1' }])
  })
})

describe('2. 建立紀錄，雲端回應成功', () => {
  it('回傳雲端資料含真實 id，草稿區為空', async () => {
    const fetch = createFakeFetch([
      { status: 201, body: [{ id: 'cloud-999', audit_content: { date: '2026-07-31', target: '王小明' }, created_at: '2026-07-31T00:00:00Z' }] }
    ])
    const store = makeStore({ fetch })

    const result = await store.records.create(sampleRecord())
    expect(result.ok).toBe(true)
    expect(result.data.id).toBe('cloud-999')

    const pending = store.records.listPending()
    expect(pending.data).toHaveLength(0)
  })
})

describe('3. 建立紀錄時連線中斷', () => {
  it('回傳 kind=network，不拋出例外', async () => {
    const fetch = createFakeFetch([{ throws: new TypeError('Failed to fetch') }])
    const store = makeStore({ fetch })

    let thrown = null
    let result
    try {
      result = await store.records.create(sampleRecord())
    } catch (e) {
      thrown = e
    }
    expect(thrown).toBeNull()
    expect(result.ok).toBe(false)
    expect(result.error.kind).toBe('network')
  })
})

describe('4. 刪除紀錄，雲端回應失敗', () => {
  it('回傳失敗，紀錄仍存在於快照中', async () => {
    const storage = createFakeStorage()
    storage.setItem('ds_v1:user-1:records:snapshot', JSON.stringify([{ id: 'rec-1' }, { id: 'rec-2' }]))
    const fetch = createFakeFetch([{ status: 403 }])
    const store = makeStore({ fetch, storage })

    const result = await store.records.deleteRecord('rec-1')
    expect(result.ok).toBe(false)
    expect(result.error.kind).toBe('forbidden')

    const snapshot = store.records.getCachedSnapshot()
    expect(snapshot.data.map(r => r.id)).toEqual(['rec-1', 'rec-2'])
  })
})

describe('5. 刪除紀錄成功', () => {
  it('快照中不再有該紀錄', async () => {
    const storage = createFakeStorage()
    storage.setItem('ds_v1:user-1:records:snapshot', JSON.stringify([{ id: 'rec-1' }, { id: 'rec-2' }]))
    const fetch = createFakeFetch([{ status: 204 }])
    const store = makeStore({ fetch, storage })

    const result = await store.records.deleteRecord('rec-1')
    expect(result.ok).toBe(true)

    const snapshot = store.records.getCachedSnapshot()
    expect(snapshot.data.map(r => r.id)).toEqual(['rec-2'])
  })
})

describe('6. 批次刪除部分失敗', () => {
  it('如實區分成功與失敗的 id，快照只移除成功的那筆', async () => {
    const storage = createFakeStorage()
    storage.setItem('ds_v1:user-1:records:snapshot', JSON.stringify([{ id: 'a' }, { id: 'b' }, { id: 'c' }]))
    const fetch = createFakeFetch([{ status: 204 }, { status: 500 }, { status: 204 }])
    const store = makeStore({ fetch, storage })

    const ids = ['a', 'b', 'c']
    const results = []
    for (const id of ids) {
      results.push({ id, result: await store.records.deleteRecord(id) })
    }

    expect(results.map(r => r.result.ok)).toEqual([true, false, true])
    const snapshot = store.records.getCachedSnapshot()
    expect(snapshot.data.map(r => r.id)).toEqual(['b'])
  })
})

describe('7. 本機快取內容損毀', () => {
  it('讀取回傳 cache-corrupt，不拋例外', () => {
    const storage = createFakeStorage()
    storage._corrupt('ds_v1:user-1:records:snapshot')
    const store = makeStore({ fetch: createFakeFetch([]), storage })

    let thrown = null
    let result
    try {
      result = store.records.getCachedSnapshot()
    } catch (e) {
      thrown = e
    }
    expect(thrown).toBeNull()
    expect(result.ok).toBe(false)
    expect(result.error.kind).toBe('cache-corrupt')
  })
})

describe('8. 本機儲存容量不足', () => {
  it('寫入回傳 cache-full；仍把本次讀到的資料回傳給呼叫端顯示', async () => {
    const storage = createFakeStorage()
    storage._setFailOnSet(true)
    const fetch = createFakeFetch([{ status: 200, body: [] }])
    const store = makeStore({ fetch, storage })

    const result = await store.records.loadSnapshot()
    // 快取寫不進去不影響「這次」讀取的結果——呼叫端當下仍看得到資料。
    expect(result.ok).toBe(true)

    storage._setFailOnSet(false)
    const writeResult = store.records._stashPending(sampleRecord())
    expect(writeResult.ok).toBe(true)
    storage._setFailOnSet(true)
    const writeResult2 = store.records._stashPending(sampleRecord())
    expect(writeResult2.ok).toBe(false)
    expect(writeResult2.error.kind).toBe('cache-full')
  })
})

describe('9. 帳號快取命名空間隔離', () => {
  it('甲帳號寫入的快取，乙帳號讀不到', async () => {
    const storage = createFakeStorage()
    const fetchA = createFakeFetch([{ status: 200, body: [{ id: '1', audit_content: {}, created_at: '2026-01-01T00:00:00Z' }] }])
    const storeA = makeStore({ fetch: fetchA, storage, userId: 'user-A' })
    await storeA.records.loadSnapshot()

    const storeB = makeStore({ fetch: createFakeFetch([]), storage, userId: 'user-B' })
    const resultB = storeB.records.getCachedSnapshot()
    expect(resultB.ok).toBe(true)
    expect(resultB.data).toEqual([])
  })
})

describe('10. 登出清除快取', () => {
  it('clearUserCache 後，該帳號的快取讀不到資料', async () => {
    const storage = createFakeStorage()
    const fetch = createFakeFetch([{ status: 200, body: [{ id: '1', audit_content: {}, created_at: '2026-01-01T00:00:00Z' }] }])
    const store = makeStore({ fetch, storage, userId: 'user-1' })
    await store.records.loadSnapshot()
    expect(store.records.getCachedSnapshot().data).toHaveLength(1)

    store.clearUserCache('user-1')
    expect(store.records.getCachedSnapshot().data).toHaveLength(0)
  })
})

describe('11. 快照中存在雲端沒有的紀錄，不得自動上傳', () => {
  it('loadSnapshot 只送出讀取請求，不會因為本機有 pending 草稿就自動送出寫入', async () => {
    const storage = createFakeStorage()
    storage.setItem('ds_v1:user-1:records:pending', JSON.stringify([sampleRecord()]))
    const fetch = createFakeFetch([{ status: 200, body: [] }])
    const store = makeStore({ fetch, storage })

    await store.records.loadSnapshot()

    expect(fetch.calls).toHaveLength(1)
    expect(fetch.calls[0].method).toBe('GET')
    // 草稿必須原封不動留在本機，因為它從未被自動送出。
    expect(store.records.listPending().data).toHaveLength(1)
  })
})

describe('12. 人員新增只送出這一筆', () => {
  it('不出現任何刪除請求', async () => {
    const fetch = createFakeFetch([{ status: 201, body: [{ unit: '清福一館', category: '護理類', name: '陳小美' }] }])
    const store = makeStore({ fetch })

    const result = await store.personnel.upsert({ unit: '清福一館', category: '護理類', name: '陳小美' })
    expect(result.ok).toBe(true)
    expect(fetch.calls).toHaveLength(1)
    expect(fetch.calls[0].method).toBe('POST')
    expect(fetch.calls[0].url).toContain('on_conflict=unit,category,name')
  })
})

describe('13. 人員刪除只送出精確刪除', () => {
  it('URL 精確指定 unit/category/name 三個條件', async () => {
    const fetch = createFakeFetch([{ status: 204 }])
    const store = makeStore({ fetch })

    const result = await store.personnel.remove({ unit: '清福一館', category: '護理類', name: '陳小美' })
    expect(result.ok).toBe(true)
    expect(fetch.calls).toHaveLength(1)
    expect(fetch.calls[0].method).toBe('DELETE')
    expect(fetch.calls[0].url).toContain('unit=eq.')
    expect(fetch.calls[0].url).toContain('category=eq.')
    expect(fetch.calls[0].url).toContain('name=eq.')
  })
})

describe('14. 人員同步失敗不留下部分狀態', () => {
  it('失敗時只送出一次請求（單一 upsert，非先刪後插）', async () => {
    const fetch = createFakeFetch([{ status: 500 }])
    const store = makeStore({ fetch })

    const result = await store.personnel.upsert({ unit: '清福一館', category: '護理類', name: '陳小美' })
    expect(result.ok).toBe(false)
    expect(fetch.calls).toHaveLength(1)
    expect(fetch.calls[0].method).toBe('POST')
  })
})

describe('15. 讀取超過單頁上限', () => {
  it('自動分頁累加，回傳完整資料', async () => {
    const page1 = Array.from({ length: 1000 }, (_, i) => ({ id: `p1-${i}`, audit_content: {}, created_at: '2026-01-01T00:00:00Z' }))
    const page2 = Array.from({ length: 234 }, (_, i) => ({ id: `p2-${i}`, audit_content: {}, created_at: '2026-01-01T00:00:00Z' }))
    const fetch = createFakeFetch([
      { status: 200, body: page1 },
      { status: 200, body: page2 }
    ])
    const store = makeStore({ fetch })

    const result = await store.records.loadSnapshot()
    expect(result.ok).toBe(true)
    expect(result.data).toHaveLength(1234)
    expect(fetch.calls).toHaveLength(2)
    expect(fetch.calls[0].url).toContain('offset=0')
    expect(fetch.calls[1].url).toContain('offset=1000')
  })
})

describe('16. 讀取某一頁失敗', () => {
  it('整體回報失敗，不回傳殘缺資料', async () => {
    const page1 = Array.from({ length: 1000 }, (_, i) => ({ id: `p1-${i}`, audit_content: {}, created_at: '2026-01-01T00:00:00Z' }))
    const fetch = createFakeFetch([
      { status: 200, body: page1 },
      { status: 500 }
    ])
    const store = makeStore({ fetch })

    const result = await store.records.loadSnapshot()
    expect(result.ok).toBe(false)
    expect(result.error.kind).toBe('network')
  })
})

describe('17. 批次寫入超過分批大小', () => {
  it('依分批大小送出對應批數，逐批回報成敗', async () => {
    const recs = Array.from({ length: 250 }, () => sampleRecord())
    const fetch = createFakeFetch([{ status: 201 }, { status: 500 }, { status: 201 }])
    const store = makeStore({ fetch })

    const results = await store.records.createMany(recs, 100)
    expect(fetch.calls).toHaveLength(3)
    expect(results.map(r => r.ok)).toEqual([true, false, true])
  })
})

describe('18. 請求標頭絕不含 service_role 憑證', () => {
  it('固定測試：所有請求的 apikey/Authorization 只會是注入的使用者憑證', async () => {
    const fetch = createFakeFetch([
      { status: 200, body: [] },
      { status: 201, body: [{ id: '1', audit_content: {}, created_at: '2026-01-01T00:00:00Z' }] },
      { status: 204 },
      { status: 201, body: [{ unit: 'x', category: 'y', name: 'z' }] }
    ])
    const store = makeStore({ fetch })

    await store.records.loadSnapshot()
    await store.records.create(sampleRecord())
    await store.records.deleteRecord('1')
    await store.personnel.upsert({ unit: 'x', category: 'y', name: 'z' })

    for (const call of fetch.calls) {
      expect(call.headers.apikey).toBe(SUPABASE_KEY)
      expect(call.headers.Authorization).toBe('Bearer user-token-123')
      // service_role JWT 的固定特徵字串，防止未來又把它埋回程式碼裡。
      expect(JSON.stringify(call.headers)).not.toMatch(/service_role/i)
      expect(JSON.stringify(call.headers)).not.toMatch(/^eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9/)
    }
  })
})

describe('未登入時的行為', () => {
  it('沒有 access token 時，寫入操作回傳 auth 錯誤，不發送任何請求', async () => {
    const fetch = createFakeFetch([])
    const store = createDataStore({
      fetch,
      storage: createFakeStorage(),
      supabaseUrl: SUPABASE_URL,
      supabaseKey: SUPABASE_KEY,
      getAccessToken: () => null,
      getUserId: () => null
    })

    const result = await store.records.deleteRecord('1')
    expect(result.ok).toBe(false)
    expect(result.error.kind).toBe('auth')
    expect(fetch.calls).toHaveLength(0)
  })

  it('建立紀錄時未登入，資料沒有遺失（存成本機草稿），並在結果中標示 pending', async () => {
    const store = createDataStore({
      fetch: createFakeFetch([]),
      storage: createFakeStorage(),
      supabaseUrl: SUPABASE_URL,
      supabaseKey: SUPABASE_KEY,
      getAccessToken: () => null,
      getUserId: () => null
    })

    const result = await store.records.create(sampleRecord())
    expect(result.ok).toBe(true)
    expect(result.data.pending).toBe(true)
    expect(store.records.listPending().data).toHaveLength(1)
  })
})

describe('重複紀錄衝突', () => {
  it('雲端回傳 409 時分類為 conflict', async () => {
    const fetch = createFakeFetch([{ status: 409, body: { message: 'duplicate key value violates unique constraint' } }])
    const store = makeStore({ fetch })

    const result = await store.records.create(sampleRecord())
    expect(result.error.kind).toBe('conflict')
  })
})
