import sys
import os
import socket
import threading
import subprocess
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler

# 獲取打包後的資源路徑
def get_resource_path():
    if hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    return os.path.abspath(".")

base_dir = get_resource_path()

# 自訂 HTTP Handler，指定根目錄為資源目錄
class CustomHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=base_dir, **kwargs)
    
    # 關閉 log 輸出，避免干擾
    def log_message(self, format, *args):
        pass

# 啟動本地伺服器
def start_server(server):
    server.serve_forever()

def main():
    # 尋找可用的 port
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('127.0.0.1', 0))
    port = s.getsockname()[1]
    s.close()

    # 建立 HTTP Server
    server = HTTPServer(('127.0.0.1', port), CustomHandler)

    # 在背景執行緒啟動 HTTP Server
    server_thread = threading.Thread(target=start_server, args=(server,), daemon=True)
    server_thread.start()

    url = f"http://127.0.0.1:{port}/index.html"

    # 尋找 Google Chrome 路徑
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
    ]
    
    chrome_exe = None
    for path in chrome_paths:
        if os.path.exists(path):
            chrome_exe = path
            break
            
    if chrome_exe:
        # 使用 Chrome 獨立視窗 (App 模式) 開啟
        try:
            process = subprocess.Popen([chrome_exe, f"--app={url}"])
            process.wait()  # 等待 Chrome 視窗關閉
        except Exception:
            import webbrowser
            webbrowser.open(url)
            while True: time.sleep(1)
    else:
        # 找不到 Chrome 時，退回使用系統預設瀏覽器
        import webbrowser
        webbrowser.open(url)
        while True: time.sleep(1)

if __name__ == "__main__":
    main()
