import re
with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Fix the missing backticks in the fetch URL
text = text.replace("fetch(${supabaseUrl}/rest/v1/audit_records, {", "fetch(`${supabaseUrl}/rest/v1/audit_records`, {")

# Fix the missing backticks in Authorization Bearer
text = text.replace("'Authorization': Bearer ,", "'Authorization': `Bearer ${session.access_token}`,")

# Fix the missing quote in console.error
text = re.sub(r"console\.error\('[^']*, e\);", "console.error('同步匯入資料至雲端失敗', e);", text)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(text)
print('Done')
