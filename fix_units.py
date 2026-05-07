import re

with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update EMAIL_TO_UNIT_MAP and ALL_UNITS to be dynamic
# We will inject the code right after ALL_UNITS definition
old_all_units = """        const ALL_UNITS = [
            '生福課',
            '清福一館', '清福二館', '清福三館',
            '清福養老院', '清春養老院', '清山養老院', '清氣養老院', '清日養老院', '清泉養老院', '清心養老院', '清照養老院', '清水養老院', '清平養老院', '清風養老院', '清清養老院', '清安養老院', '清景養老院', '清涼養老院',
            '清福護理之家'
        ];"""

new_all_units = """        const BASE_EMAIL_TO_UNIT_MAP = {
            'hok6@hok2.com.tw': '清山養老院', 'hok3@hok2.com.tw': '清心養老院', 'hok7@hok1.com.tw': '清日養老院',
            'hok11@hok3.com.tw': '清水養老院', 'hok4@hok2.com.tw': '清平養老院', 'hok8@hok1.com.tw': '清安養老院',
            'hok5@hok2.com.tw': '清春養老院', 'hok9@hok3.com.tw': '清泉養老院', 'hok15@hok6.com.tw': '清風養老院',
            'hok2@hok2.com.tw': '清氣養老院', 'hok13@hok6.com.tw': '清涼養老院', 'hok12@hok6.com.tw': '清清養老院',
            'hok14@hok6.com.tw': '清景養老院', 'hok10@hok3.com.tw': '清照養老院', 'hok16@hok6.com.tw': '清福一館',
            'hok17@hok6.com.tw': '清福二館', 'hok18@hok6.com.tw': '清福三館', 'hok1@hok2.com.tw': '清福養老院',
            'hok2f@hok6.com.tw': '清福護理之家',
            'test@hok6.com.tw': '測試機構'
        };

        const BASE_ALL_UNITS = [
            '生福課',
            '清福一館', '清福二館', '清福三館',
            '清福養老院', '清春養老院', '清山養老院', '清氣養老院', '清日養老院', '清泉養老院', '清心養老院', '清照養老院', '清水養老院', '清平養老院', '清風養老院', '清清養老院', '清安養老院', '清景養老院', '清涼養老院',
            '清福護理之家', '測試機構'
        ];
        
        let customUnitsCache = [];
        try {
            customUnitsCache = JSON.parse(localStorage.getItem('audit_custom_units_v1') || '[]');
        } catch(e){}

        const EMAIL_TO_UNIT_MAP = { ...BASE_EMAIL_TO_UNIT_MAP };
        const ALL_UNITS = [ ...BASE_ALL_UNITS ];
        
        customUnitsCache.forEach(cu => {
            if (cu.email) EMAIL_TO_UNIT_MAP[cu.email.toLowerCase()] = cu.unit;
            if (!ALL_UNITS.includes(cu.unit)) ALL_UNITS.push(cu.unit);
        });
"""

# Replace the old definition of EMAIL_TO_UNIT_MAP
content = re.sub(r"const EMAIL_TO_UNIT_MAP = \{[\s\S]*?\};\s*const ALL_UNITS = \[[\s\S]*?\];", new_all_units, content)

# 2. Add saveCustomUnits / getCustomUnits to Storage
old_storage = "getPersonnel: () => JSON.parse(localStorage.getItem('audit_personnel_v1') || '{}')"
new_storage = "getPersonnel: () => JSON.parse(localStorage.getItem('audit_personnel_v1') || '{}'),\n            saveCustomUnits: (data) => localStorage.setItem('audit_custom_units_v1', JSON.stringify(data)),\n            getCustomUnits: () => JSON.parse(localStorage.getItem('audit_custom_units_v1') || '[]')"
content = content.replace(old_storage, new_storage)

# 3. Fix line 735 hardcoded check
old_735 = "if (['清福養老院', '清春養老院', '清山養老院', '清氣養老院', '清日養老院', '清泉養老院', '清心養老院', '清照養老院', '清水養老院', '清平養老院', '清風養老院', '清清養老院', '清安養老院', '清景養老院', '清涼養老院', '清福護理之家'].includes(u)) {"
new_735 = "if (ALL_UNITS.includes(u)) {"
content = content.replace(old_735, new_735)

# 4. Find and replace hardcoded <option> blocks
# They start with <option value="清福養老院"> and end with </option> multiple lines.
# Instead of regex matching the entire block, we'll replace the first option with ALL_UNITS.map and delete the rest.

# Let's replace the whole selects or options
import re
content = re.sub(
    r'<option value="清福養老院">清福養老院</option>.*?<option value="清福護理之家">清福護理之家</option>',
    r'{ALL_UNITS.filter(u => u !== "生福課").map(u => <option key={u} value={u}>{u}</option>)}',
    content,
    flags=re.DOTALL
)

# Wait, there are some blocks that have different formatting. Let's see how many were replaced.
with open("index.html", "w", encoding="utf-8") as f:
    f.write(content)

print("Phase 1 done.")
