import re

filepath = 'index.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Fix the debug info state and logic with escaped unicode
content = content.replace("const [debugInfo, setDebugInfo] = React.useState('');", 
                          "const [debugInfo, setDebugInfo] = useState('');")

# Replace the mangled setDebugInfo line
# It looks like: setDebugInfo(`?脩垢?勗???${recs.length} 蝑????函?璈???[${sessUnit}]`);
content = re.sub(r"setDebugInfo\(`.*?${recs\.length}.*?\${sessUnit}.*?`\);", 
                 "setDebugInfo(`\\u96f2\\u7aef\\u5171\\u56de\\u50b3 ${recs.length} \\u7b46\\u8cc7\\u6599\\uff0c\\u60a8\\u7684\\u6a5f\\u69cb\\u70ba [${sessUnit}]`);", content)

# 2. Fix the UI element
content = content.replace('{debugInfo || "甇?頛?脩垢閮箸鞈?..."}', 
                          '{debugInfo || "\\u6b63\\u5728\\u8f09\\u5165\\u96f2\\u7aef\\u8a3a\\u65b7\\u8cc7\\u8a0a..."}')

# 3. Robust Filter Logic (Strip non-Chinese characters for comparison)
robust_filter = """
                    const normalize = (s) => String(s || '').replace(/[^\\u4e00-\\u9fa5]/g, '');
                    const rUnitNorm = normalize(r.unit);
                    const fUnitNorm = normalize(filterUnit);
                    return (filterMonth ? String(r.date).startsWith(filterMonth) : true) &&
                        (filterItem ? r.auditName === filterItem : true) &&
                        (filterUnit ? (rUnitNorm.includes(fUnitNorm) || fUnitNorm.includes(rUnitNorm)) : (filterUnitCategory ? uCat === filterUnitCategory : true));
"""

# Replace the current filter logic in flatFilteredRecords
# Pattern matches the return statement inside the filter
content = re.sub(r"return \(filterMonth \? String\(r\.date\)\.startsWith\(filterMonth\) : true\) &&\s*\(filterItem \? r\.auditName === filterItem : true\) &&\s*\(filterUnit \? .*? : \(filterUnitCategory \? uCat === filterUnitCategory : true\)\);",
                 robust_filter.strip(), content)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print('Robust filter and escaped unicode diagnostics applied.')
