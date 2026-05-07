"""
部署 index.html 到 Netlify (使用 Netlify API 手動部署)
無需 Node.js，僅需 Python + requests
"""
import hashlib
import json
import os
import sys
import urllib.request
import urllib.error

# Fix Windows console encoding
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

SITE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_NAME = "index.html"
FILE_PATH = os.path.join(SITE_DIR, FILE_NAME)

def sha1_file(path):
    h = hashlib.sha1()
    with open(path, 'rb') as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

def deploy():
    if not os.path.exists(FILE_PATH):
        print(f"[ERROR] File not found: {FILE_PATH}")
        sys.exit(1)

    file_hash = sha1_file(FILE_PATH)
    print(f"[PACK] Preparing {FILE_NAME} ({os.path.getsize(FILE_PATH):,} bytes)")
    print(f"   SHA1: {file_hash}")

    print("\n[WEB] Creating site on Netlify...")
    deploy_data = json.dumps({
        "files": {
            f"/{FILE_NAME}": file_hash
        }
    }).encode('utf-8')

    req = urllib.request.Request(
        "https://api.netlify.com/api/v1/sites",
        data=deploy_data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as resp:
            site_info = json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"[ERROR] Create site failed: {e.code} {e.read().decode()}")
        sys.exit(1)

    site_id = site_info.get("id", "")
    deploy_id = site_info.get("deploy_id", "")
    site_url = site_info.get("ssl_url") or site_info.get("url", "")

    print(f"   [OK] Site ID: {site_id}")
    print(f"   [OK] Deploy ID: {deploy_id}")

    print(f"\n[UPLOAD] Uploading {FILE_NAME}...")
    with open(FILE_PATH, 'rb') as f:
        file_content = f.read()

    upload_url = f"https://api.netlify.com/api/v1/deploys/{deploy_id}/files/{FILE_NAME}"
    req2 = urllib.request.Request(
        upload_url,
        data=file_content,
        headers={"Content-Type": "application/octet-stream"},
        method="PUT"
    )

    try:
        with urllib.request.urlopen(req2) as resp:
            resp.read()
        print("   [OK] Upload success!")
    except urllib.error.HTTPError as e:
        print(f"[ERROR] Upload failed: {e.code} {e.read().decode()}")
        sys.exit(1)

    print(f"\n{'='*50}")
    print(f"[DONE] Deploy complete!")
    print(f"[URL]  {site_url}")
    print(f"{'='*50}")
    
    info_path = os.path.join(SITE_DIR, "netlify_site_info.json")
    with open(info_path, 'w', encoding='utf-8') as f:
        json.dump({"site_id": site_id, "deploy_id": deploy_id, "url": site_url}, f, indent=2)
    print(f"[INFO] Site info saved to: netlify_site_info.json")

if __name__ == "__main__":
    deploy()

