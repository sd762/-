import re

filepath = 'index.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace EVERYTHING inside catch (e) { ... } before the next closing brace
content = re.sub(r'catch \(e\) \{[^}]*\}', 'catch (e) { console.error("Failed", e); }', content)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print('Syntax errors fixed')
