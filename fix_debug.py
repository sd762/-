import re

filepath = 'index.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add debug state to the App component
content = content.replace("const [dialog, setDialog] = useState({ isOpen: false, title: '', message: '', type: 'info' });", 
                          "const [dialog, setDialog] = useState({ isOpen: false, title: '', message: '', type: 'info' });\n            const [debugInfo, setDebugInfo] = useState('');")

# 2. Update loadAllDataFromCloud to set debug info
content = re.sub(r"console\.log\('\\u8b80\\u53d6\\u7d00\\u9304\\u6578\\u91cf:', recs\.length\);", 
                 "console.log('讀取紀錄數量:', recs.length); setDebugInfo(`雲端共回傳 ${recs.length} 筆資料，您的機構為 [${sessUnit}]`);", content)

# 3. Even looser filter logic
content = content.replace("filterUnit ? String(r.unit || '').trim() === String(filterUnit || '').trim() :", 
                          "filterUnit ? (String(r.unit || '').trim().includes(String(filterUnit || '').trim()) || String(filterUnit || '').trim().includes(String(r.unit || '').trim())) :")

# 4. Show debug info in the UI
content = content.replace('<div className="mt-8 text-center text-slate-300 text-[10px]">', 
                          '<div className="mt-4 p-2 bg-slate-50 rounded text-[10px] text-slate-400 text-center border border-dashed border-slate-200">{debugInfo || "正在連線雲端..."}</div>\n                            <div className="mt-8 text-center text-slate-300 text-[10px]">')

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print('Debug mode and loose filtering enabled.')
