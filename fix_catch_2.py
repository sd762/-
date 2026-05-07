import re

filepath = 'index.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace any line containing console.error with a broken string in the catch block
# We know the catch block is roughly: } catch (e) { console.error('...', e); }
content = re.sub(r"console\.error\('[^'\n]*?, e\);", "console.error('Failed to sync', e);", content)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print('Syntax errors fixed')
