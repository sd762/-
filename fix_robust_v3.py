filepath = 'index.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. State
content = content.replace("const [debugInfo, setDebugInfo] = React.useState('');", "const [debugInfo, setDebugInfo] = useState('');")

# 2. Sync logic - find the line by its parts
import re
# Match the corrupted setDebugInfo line
content = re.sub(r'setDebugInfo\(`.*?recs\.length.*?sessUnit.*?`\);', 
                 'setDebugInfo(`\\u96f2\\u7aef\\u5171\\u56de\\u50b3 ${recs.length} \\u7b46\\u8cc7\\u6599\\uff0c\\u60a8\\u7684\\u6a5f\\u69cb\\u70ba [${sessUnit}]`);'.replace('\\', '\\\\'), 
                 content)

# 3. UI logic
# The corrupted string is very unique
content = re.sub(r'\{debugInfo \|\| ".*?"\}', 
                 '{debugInfo || "\\u6b63\\u5728\\u8f09\\u5165\\u96f2\\u7aef\\u8a3a\\u65b7\\u8cc7\\u8a0a..."}'.replace('\\', '\\\\'), 
                 content)

# 4. Filter logic
# Just replace the return statement that matches the pattern
old_return_pattern = r"return \(filterMonth \? String\(r\.date\)\.startsWith\(filterMonth\) : true\) &&\s*\(filterItem \? r\.auditName === filterItem : true\) &&\s*\(filterUnit \? .*? : \(filterUnitCategory \? uCat === filterUnitCategory : true\)\);"

new_return = """
                    const normalize = (s) => String(s || '').replace(/[^\\u4e00-\\u9fa5]/g, '');
                    const rUnitNorm = normalize(r.unit);
                    const fUnitNorm = normalize(filterUnit);
                    return (filterMonth ? String(r.date).startsWith(filterMonth) : true) &&
                        (filterItem ? r.auditName === filterItem : true) &&
                        (filterUnit ? (rUnitNorm.includes(fUnitNorm) || fUnitNorm.includes(rUnitNorm)) : (filterUnitCategory ? uCat === filterUnitCategory : true));
""".strip().replace('\\', '\\\\')

content = re.sub(old_return_pattern, new_return, content)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print('Done')
