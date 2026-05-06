import sys
import os
import subprocess

def main():
    # 改為直接指向您在 GitHub Pages 上的網址
    url = "https://sd762.github.io/-/"

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
        # 使用 Chrome 獨立視窗 (App 模式) 開啟遠端網址
        try:
            subprocess.Popen([chrome_exe, f"--app={url}"])
        except Exception:
            import webbrowser
            webbrowser.open(url)
    else:
        # 找不到 Chrome 時，退回使用系統預設瀏覽器
        import webbrowser
        webbrowser.open(url)

if __name__ == "__main__":
    main()
