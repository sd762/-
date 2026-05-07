import re

filepath = 'index.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Fix the debug info state and logic with escaped unicode
content = content.replace("const [debugInfo, setDebugInfo] = React.useState('');", 
                          "const [debugInfo, setDebugInfo] = useState('');")

# 2. Fix setDebugInfo call
# Using a simpler string replacement for the mangled line
import re
target_pattern = r"setDebugInfo\(`.*?recs\.length.*?sessUnit.*?`\);"
replacement_line = "setDebugInfo(`\\u96f2\\u7aef\\u5171\\u56de\\u50b3 ${recs.length} \\u7b46\\u8cc7\\u6599\\uff0c\\u60a8\\u7684\\u6a5f\\u69cb\\u70ba [${sessUnit}]`);"
# Escaping for re.sub: backslashes need to be doubled for Python string AND for re.sub
replacement_for_sub = replacement_line.replace('\\', '\\\\')

content = re.sub(target_pattern, replacement_for_sub, content)

# 3. Fix the UI element
# The mangled text was "甇?頛?脩垢閮箸鞈?..."
# Let's just find the part that looks like it
content = re.sub(r'\{debugInfo \|\| ".*?"\}', 
                 '{debugInfo || "\\u6b63\\u5728\\u8f09\\u5165\\u96f2\\u7aef\\u8a3a\\u65b7\\u8cc7\\u8a0a..."}', content)

# 4. Robust Filter Logic
robust_filter = """
                    const normalize = (s) => String(s || '').replace(/[^\\u4e00-\\u9fa5]/g, '');
                    const rUnitNorm = normalize(r.unit);
                    const fUnitNorm = normalize(filterUnit);
                    return (filterMonth ? String(r.date).startsWith(filterMonth) : true) &&
                        (filterItem ? r.auditName === filterItem : true) &&
                        (filterUnit ? (rUnitNorm.includes(fUnitNorm) || fUnitNorm.includes(rUnitNorm)) : (filterUnitCategory ? uCat === filterUnitCategory : true));
"""

# Find the filter block in flatFilteredRecords
# It starts with return records.filter(r => {
# and ends with });
# I'll just replace the specific return statement inside it.
pattern_return = r"return \(filterMonth \? String\(r\.date\)\.startsWith\(filterMonth\) : true\) &&\s*\(filterItem \? r\.auditName === filterItem : true\) &&\s*\(filterUnit \? .*? : \(filterUnitCategory \? uCat === filterUnitCategory : true\)\);"
content = re.sub(pattern_return, robust_filter.strip().replace('\\', '\\\\'), content)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print('Success')
