import requests
import json

SUPABASE_URL = "https://khkvqkbssngclojtxkuv.supabase.co"
SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtoa3Zxa2Jzc25nY2xvanR4a3V2Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3ODAyMTgwOSwiZXhwIjoyMDkzNTk3ODA5fQ._kgSuOGrqQWgPQcrn0kl9pDWcWCPKyZVGfYyDQa3D0g"

users = [
    "hok6@hok2.com.tw", "hok3@hok2.com.tw", "hok7@hok1.com.tw",
    "hok11@hok3.com.tw", "hok4@hok2.com.tw", "hok8@hok2.com.tw",
    "hok5@hok2.com.tw", "hok9@hok3.com.tw", "hok15@hok6.com.tw",
    "hok2@hok2.com.tw", "hok13@hok6.com.tw", "hok12@hok6.com.tw",
    "hok14@hok6.com.tw", "hok10@hok3.com.tw", "hok16@hok6.com.tw",
    "hok17@hok6.com.tw", "hok18@hok6.com.tw", "hok1@hok2.com.tw",
    "hok2f@hok6.com.tw"
]

password = "000000"

headers = {
    "apikey": SERVICE_ROLE_KEY,
    "Authorization": f"Bearer {SERVICE_ROLE_KEY}",
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
