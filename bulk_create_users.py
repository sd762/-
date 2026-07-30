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
#     set SUPABASE_SECRET_KEY=<新版 sb_secret_... 金鑰>
#     set NEW_USER_PASSWORD=<該帳號的隨機密碼>
#     python bulk_create_users.py

import json
import os
import sys

import requests

SUPABASE_URL = "https://khkvqkbssngclojtxkuv.supabase.co"

SECRET_KEY = os.environ.get("SUPABASE_SECRET_KEY", "").strip()
if not SECRET_KEY:
    print("錯誤：找不到環境變數 SUPABASE_SECRET_KEY。")
    sys.exit(1)

password = os.environ.get("NEW_USER_PASSWORD", "").strip()
if len(password) < 12:
    print("錯誤：NEW_USER_PASSWORD 未設定或長度不足 12 字元。")
    print("請勿使用共用或易猜的密碼。")
    sys.exit(1)

users = [
    "hok6@hok2.com.tw", "hok3@hok2.com.tw", "hok7@hok1.com.tw",
    "hok11@hok3.com.tw", "hok4@hok2.com.tw", "hok8@hok2.com.tw",
    "hok5@hok2.com.tw", "hok9@hok3.com.tw", "hok15@hok6.com.tw",
    "hok2@hok2.com.tw", "hok13@hok6.com.tw", "hok12@hok6.com.tw",
    "hok14@hok6.com.tw", "hok10@hok3.com.tw", "hok16@hok6.com.tw",
    "hok17@hok6.com.tw", "hok18@hok6.com.tw", "hok1@hok2.com.tw",
    "hok2f@hok6.com.tw"
]

headers = {
    "apikey": SECRET_KEY,
    "Authorization": f"Bearer {SECRET_KEY}",
    "Content-Type": "application/json"
}

results = []

for email in users:
    print(f"Creating user: {email}...")
    url = f"{SUPABASE_URL}/auth/v1/admin/users"
    data = {
        "email": email,
        "password": password,
        "email_confirm": True
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 201:
        print(f"Success: {email}")
        results.append(f"SUCCESS: {email}")
    else:
        print(f"Failed: {email} - {response.text}")
        results.append(f"FAILED: {email} ({response.text})")

print("\n--- Summary ---")
for r in results:
    print(r)
