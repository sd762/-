import re

filepath = 'index.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove unit filter in loadAllDataFromCloud
old_sync = """                    // 1. 讀取稽核紀錄
                    let url = `${supabaseUrl}/rest/v1/audit_records?select=*&order=audit_date.desc`;
                    if (!sessCanViewAll && sessUnit) {
                        url += `&unit=eq.${encodeURIComponent(sessUnit)}`;
                    }
                    const recRes = await fetch(url, { headers });"""

new_sync = """                    // 1. 讀取稽核紀錄 (後端不帶過濾條件，由前端處理，避免編碼不一致)
                    let url = `${supabaseUrl}/rest/v1/audit_records?select=*&order=audit_date.desc`;
                    const recRes = await fetch(url, { headers });"""

content = content.replace(old_sync, new_sync)

# 2. Update filtering logic for unit matching (robust against spaces)
# Pattern: (filterUnit ? r.unit === filterUnit : (filterUnitCategory ? uCat === filterUnitCategory : true))
# Replacement: (filterUnit ? String(r.unit || '').trim() === String(filterUnit || '').trim() : (filterUnitCategory ? uCat === filterUnitCategory : true))

filter_pattern = r"\(filterUnit \? r\.unit === filterUnit : \(filterUnitCategory \? uCat === filterUnitCategory : true\)\)"
filter_replacement = "(filterUnit ? String(r.unit || '').trim() === String(filterUnit || '').trim() : (filterUnitCategory ? uCat === filterUnitCategory : true))"

content = re.sub(filter_pattern, filter_replacement, content)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print('Bypass API filter and robustify unit matching complete.')
