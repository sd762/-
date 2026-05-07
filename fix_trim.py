import re

filepath = 'index.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Trim units in sync logic (uploading)
content = content.replace("unit: r.unit,", "unit: String(r.unit || '').trim(),")
content = content.replace("unit: newRec.unit,", "unit: String(newRec.unit || '').trim(),")
content = content.replace("unit: finalUnit,", "unit: String(finalUnit || '').trim(),")

# Also trim when setting state for syncWithCloud
content = content.replace("unit: r.unit || '',", "unit: String(r.unit || '').trim(),")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print('Trimming complete.')
