import os
import re

filepath = 'index.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('fetch(/rest/v1/audit_records, {', 'fetch(`${supabaseUrl}/rest/v1/audit_records`, {'.replace('`', ''))
content = content.replace(\"'Authorization': Bearer ,\", \"'Authorization': `Bearer `,\".replace('`', ''))

# Replace broken console.error line
content = re.sub(r\"console\.error\('.*?, e\);\", \"console.error('Failed to sync', e);\", content)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print('Syntax errors fixed')
