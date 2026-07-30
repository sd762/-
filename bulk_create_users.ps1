# 批次建立使用者帳號（一次性工具，帳號已於 2026 年建立完畢）
#
# ── 安全性注意 ────────────────────────────────────────────────
# 本檔先前將 service_role 金鑰與密碼直接寫死在原始碼中，而本 repo 為公開，
# 等同對外公布「金鑰 + 帳號清單 + 密碼」。該金鑰已於 2026-07-30 停用。
#
# 金鑰與密碼一律改由環境變數傳入，不得再寫回檔案。
# 密碼請使用每個帳號各自不同的隨機值，切勿沿用共用密碼。
#
# 使用方式：
#     $env:SUPABASE_SECRET_KEY = "<新版 sb_secret_... 金鑰>"
#     $env:NEW_USER_PASSWORD   = "<該帳號的隨機密碼>"
#     .\bulk_create_users.ps1

$ErrorActionPreference = 'Stop'

$url = "https://khkvqkbssngclojtxkuv.supabase.co/auth/v1/admin/users"

$key = $env:SUPABASE_SECRET_KEY
if ([string]::IsNullOrWhiteSpace($key)) {
    Write-Host '錯誤：找不到環境變數 SUPABASE_SECRET_KEY。' -ForegroundColor Red
    exit 1
}

$password = $env:NEW_USER_PASSWORD
if ([string]::IsNullOrWhiteSpace($password) -or $password.Length -lt 12) {
    Write-Host '錯誤：NEW_USER_PASSWORD 未設定或長度不足 12 字元。' -ForegroundColor Red
    Write-Host '請勿使用共用或易猜的密碼。'
    exit 1
}

$users = @(
    "hok6@hok2.com.tw", "hok3@hok2.com.tw", "hok7@hok1.com.tw",
    "hok11@hok3.com.tw", "hok4@hok2.com.tw", "hok8@hok2.com.tw",
    "hok5@hok2.com.tw", "hok9@hok3.com.tw", "hok15@hok6.com.tw",
    "hok2@hok2.com.tw", "hok13@hok6.com.tw", "hok12@hok6.com.tw",
    "hok14@hok6.com.tw", "hok10@hok3.com.tw", "hok16@hok6.com.tw",
    "hok17@hok6.com.tw", "hok18@hok6.com.tw", "hok1@hok2.com.tw",
    "hok2f@hok6.com.tw"
)

$headers = @{
    "apikey"        = $key
    "Authorization" = "Bearer $key"
    "Content-Type"  = "application/json"
}

foreach ($email in $users) {
    Write-Host "Creating user: $email..."
    $body = @{
        "email"         = $email
        "password"      = $password
        "email_confirm" = $true
    } | ConvertTo-Json

    try {
        $null = Invoke-RestMethod -Uri $url -Method Post -Headers $headers -Body $body
        Write-Host "Success: $email"
    } catch {
        Write-Host "Failed: $email - $($_.Exception.Message)"
    }
}
