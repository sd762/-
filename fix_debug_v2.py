import re

filepath = 'index.html'
with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 1. Add state (search for first useState)
for i in range(1318, 1400):
    if 'useState' in lines[i]:
        lines.insert(i+1, "            const [debugInfo, setDebugInfo] = React.useState('');\n")
        break

# 2. Add debug info update in loadAllDataFromCloud
# Search for the fetch logic around line 1470
for i in range(1450, 1550):
    if 'console.log' in lines[i] and 'recs.length' in lines[i]:
        lines[i] = f"                        console.log('Records loaded:', recs.length);\n                        setDebugInfo(`雲端共回傳 ${{recs.length}} 筆資料，您的機構為 [${{sessUnit}}]`);\n"
        break

# 3. Add UI element (search for the last </div> before return)
# Search backwards from line 3550
for i in range(3550, 3000, -1):
    if '</div>' in lines[i] and ');' in lines[i+1]: # End of return (
        lines.insert(i, '                    <div style={{fontSize:"10px", color:"#999", padding:"10px", textAlign:"center", borderTop:"1px dashed #eee"}}>{debugInfo || "正在載入雲端診斷資訊..."}</div>\n')
        break

with open(filepath, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('Debug UI inserted via line-based script.')
