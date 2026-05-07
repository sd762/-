filepath = 'index.html'
with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Line numbers are 1-indexed. lines[1470] is line 1471.
# Check content first
print(f"Line 1471: {lines[1470]}")

lines[1470] = "                    // 1. 讀取稽核紀錄 (後端不帶過濾條件，由前端處理，避免編碼不一致)\n"
lines[1471] = "                    let url = `${supabaseUrl}/rest/v1/audit_records?select=*&order=audit_date.desc`;\n"
lines[1472] = "" # Delete
lines[1473] = "" # Delete

# Also fix the filters
import re
filter_pattern = r"\(filterUnit \? r\.unit === filterUnit : \(filterUnitCategory \? uCat === filterUnitCategory : true\)\)"
filter_replacement = "(filterUnit ? String(r.unit || '').trim() === String(filterUnit || '').trim() : (filterUnitCategory ? uCat === filterUnitCategory : true))"

for i in range(len(lines)):
    lines[i] = re.sub(filter_pattern, filter_replacement, lines[i])

with open(filepath, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('Success')
