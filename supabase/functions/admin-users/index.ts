// 清福技術考稽核系統 —— 系統後台的使用者管理，伺服器端實作。
//
// 背景：網頁版後台原本要求管理員把 Supabase secret key 貼進瀏覽器的輸入框，
// 直接從瀏覽器呼叫 Supabase Auth Admin API。Supabase 新版金鑰系統會偵測並
// 拒絕帶瀏覽器特徵的請求（"Forbidden use of secret API key in browser"），
// 這個做法已經走不通，而且本質上就是不該做的事——secret key 從來就不該
// 進到瀏覽器。
//
// 正確做法：secret key 只存在這支 Edge Function 的伺服器端環境變數裡，
// 瀏覽器改成用「登入者自己的權杖」呼叫這支函式；函式先用 service role
// 驗證這個權杖真的對應一個管理員帳號，通過後才代為執行特權操作。
// 瀏覽器自始至終看不到 secret key。

import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const SUPABASE_URL = Deno.env.get('SUPABASE_URL')!
const SERVICE_ROLE_KEY = Deno.env.get('SERVICE_ROLE_KEY')!
const SUPER_ADMIN_EMAIL = 'sd@hok6.com.tw'

const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, content-type, apikey',
  'Access-Control-Allow-Methods': 'POST, OPTIONS'
}

function json(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' }
  })
}

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: CORS_HEADERS })
  }
  if (req.method !== 'POST') {
    return json({ error: '只接受 POST' }, 405)
  }

  const adminClient = createClient(SUPABASE_URL, SERVICE_ROLE_KEY)

  // 驗證呼叫者身分：不能信任前端聲稱的身分，一律用 service role 反查
  // 這個權杖真正對應的帳號與 app_metadata。
  const authHeader = req.headers.get('Authorization') || ''
  const callerToken = authHeader.replace(/^Bearer\s+/i, '')
  if (!callerToken) return json({ error: '缺少授權標頭' }, 401)

  const { data: callerData, error: callerErr } = await adminClient.auth.getUser(callerToken)
  if (callerErr || !callerData?.user) return json({ error: '無效的登入憑證' }, 401)

  const caller = callerData.user
  const isAdmin = caller.email === SUPER_ADMIN_EMAIL || caller.app_metadata?.role === 'admin'
  if (!isAdmin) return json({ error: '權限不足，僅系統管理員可使用此功能' }, 403)

  let action = ''
  let payload: Record<string, unknown> = {}
  try {
    const body = await req.json()
    action = body.action
    payload = body.payload || {}
  } catch {
    return json({ error: '請求內容不是合法的 JSON' }, 400)
  }

  try {
    switch (action) {
      case 'list': {
        const all: unknown[] = []
        let page = 1
        while (true) {
          const { data, error } = await adminClient.auth.admin.listUsers({ perPage: 200, page })
          if (error) return json({ error: error.message }, 500)
          all.push(...data.users)
          if (data.users.length < 200) break
          page++
        }
        return json({ users: all })
      }

      case 'create': {
        const email = String(payload.email || '').trim()
        const password = String(payload.password || '')
        const unit = String(payload.unit || '').trim()
        if (!email || !unit) return json({ error: '缺少必要欄位（email、unit）' }, 400)
        if (password.length < 6) return json({ error: '密碼需至少 6 碼' }, 400)

        const { data, error } = await adminClient.auth.admin.createUser({
          email, password, email_confirm: true,
          app_metadata: { unit, role: 'user' }
        })
        if (error) return json({ error: error.message }, 400)
        return json({ user: data.user })
      }

      case 'updateUnit': {
        const userId = String(payload.userId || '')
        const unit = String(payload.unit || '').trim()
        if (!userId || !unit) return json({ error: '缺少必要欄位（userId、unit）' }, 400)

        const { data: existing, error: getErr } = await adminClient.auth.admin.getUserById(userId)
        if (getErr || !existing?.user) return json({ error: getErr?.message || '找不到使用者' }, 404)

        const merged = { ...(existing.user.app_metadata || {}), unit }
        const { data, error } = await adminClient.auth.admin.updateUserById(userId, { app_metadata: merged })
        if (error) return json({ error: error.message }, 400)
        return json({ user: data.user })
      }

      case 'resetPassword': {
        const userId = String(payload.userId || '')
        const password = String(payload.password || '')
        if (!userId) return json({ error: '缺少必要欄位（userId）' }, 400)
        if (password.length < 6) return json({ error: '密碼需至少 6 碼' }, 400)

        const { error } = await adminClient.auth.admin.updateUserById(userId, { password })
        if (error) return json({ error: error.message }, 400)
        return json({ ok: true })
      }

      case 'updateEmail': {
        const userId = String(payload.userId || '')
        const email = String(payload.email || '').trim()
        if (!userId || !email) return json({ error: '缺少必要欄位（userId、email）' }, 400)

        const { error } = await adminClient.auth.admin.updateUserById(userId, { email, email_confirm: true })
        if (error) return json({ error: error.message }, 400)
        return json({ ok: true })
      }

      case 'delete': {
        const userId = String(payload.userId || '')
        if (!userId) return json({ error: '缺少必要欄位（userId）' }, 400)

        // 刪除帳號前一併清除該帳號建立的稽核紀錄（audit_personnel 是以
        // 機構共享，不綁個人帳號，不需要在這裡處理）。
        await adminClient.from('audit_records').delete().eq('user_id', userId)

        const { error } = await adminClient.auth.admin.deleteUser(userId)
        if (error) return json({ error: error.message }, 400)
        return json({ ok: true })
      }

      default:
        return json({ error: `未知操作：${action}` }, 400)
    }
  } catch (e) {
    console.error('admin-users 執行例外:', e)
    return json({ error: e instanceof Error ? e.message : String(e) }, 500)
  }
})
