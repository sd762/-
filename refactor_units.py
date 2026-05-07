import re

with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update EMAIL_TO_UNIT_MAP to include test@hok6.com.tw
old_email_map = """            'hok17@hok6.com.tw': '清福二館', 'hok18@hok6.com.tw': '清福三館', 'hok1@hok2.com.tw': '清福養老院',
            'hok2f@hok6.com.tw': '清福護理之家'"""
new_email_map = """            'hok17@hok6.com.tw': '清福二館', 'hok18@hok6.com.tw': '清福三館', 'hok1@hok2.com.tw': '清福養老院',
            'hok2f@hok6.com.tw': '清福護理之家', 'test@hok6.com.tw': '測試機構'"""
content = content.replace(old_email_map, new_email_map)

# 2. Update ALL_UNITS to include 測試機構
old_all_units = """            '清福養老院', '清春養老院', '清山養老院', '清氣養老院', '清日養老院', '清泉養老院', '清心養老院', '清照養老院', '清水養老院', '清平養老院', '清風養老院', '清清養老院', '清安養老院', '清景養老院', '清涼養老院',
            '清福護理之家'"""
new_all_units = """            '清福養老院', '清春養老院', '清山養老院', '清氣養老院', '清日養老院', '清泉養老院', '清心養老院', '清照養老院', '清水養老院', '清平養老院', '清風養老院', '清清養老院', '清安養老院', '清景養老院', '清涼養老院',
            '清福護理之家', '測試機構'"""
content = content.replace(old_all_units, new_all_units)

# 3. Fix getUnitCategory to be dynamic
old_getCat = """        const getUnitCategory = (unit) => {
            if (['清福一館', '清福二館', '清福三館'].includes(unit)) return '法人館';
            if (['清福養老院', '清春養老院', '清山養老院', '清氣養老院', '清日養老院', '清泉養老院', '清心養老院', '清照養老院', '清水養老院', '清平養老院', '清風養老院', '清清養老院', '清安養老院', '清景養老院', '清涼養老院'].includes(unit)) return '養護機構';
            if (unit === '清福護理之家') return '清福護理之家';
            return '';
        };"""
new_getCat = """        const getUnitCategory = (unit) => {
            if (!unit) return '';
            if (['清福一館', '清福二館', '清福三館'].includes(unit)) return '法人館';
            if (unit === '清福護理之家') return '清福護理之家';
            if (unit.includes('養老院')) return '養護機構';
            return '其他機構';
        };"""
content = content.replace(old_getCat, new_getCat)

# 4. Use user_metadata.unit if available
content = content.replace("userUnit = EMAIL_TO_UNIT_MAP[session.user.email.toLowerCase()] || '';", "userUnit = session.user?.user_metadata?.unit || EMAIL_TO_UNIT_MAP[session.user.email.toLowerCase()] || '';")
content = content.replace("sessUnit = EMAIL_TO_UNIT_MAP[sess.user.email.toLowerCase()] || '';", "sessUnit = sess.user?.user_metadata?.unit || EMAIL_TO_UNIT_MAP[sess.user.email.toLowerCase()] || '';")

# 5. Extract dynamicUnits in App component
# Find the start of App component and insert it
app_start = "const App = () => {"
app_start_new = """const App = () => {
            const [dynamicUnits, setDynamicUnits] = useState(ALL_UNITS);

            useEffect(() => {
                try {
                    const custom = JSON.parse(localStorage.getItem('custom_units_list') || '[]');
                    if (custom.length > 0) {
                        setDynamicUnits([...new Set([...ALL_UNITS, ...custom])]);
                    }
                } catch(e) {}
            }, []);
"""
content = content.replace(app_start, app_start_new)

# 6. Add UI to AdminPanel to manage dynamic units
admin_panel_start = """const AdminPanel = ({ handleTemplateUpload, handleExportBackup, handleImportBackup }) => {"""
admin_panel_new = """const AdminPanel = ({ handleTemplateUpload, handleExportBackup, handleImportBackup }) => {
            const [customUnits, setCustomUnits] = useState([]);
            const [newCustomUnit, setNewCustomUnit] = useState('');
            useEffect(() => {
                try { setCustomUnits(JSON.parse(localStorage.getItem('custom_units_list') || '[]')); } catch(e){}
            }, []);
            const handleAddCustomUnit = () => {
                if (!newCustomUnit.trim()) return;
                const updated = [...new Set([...customUnits, newCustomUnit.trim()])];
                setCustomUnits(updated);
                localStorage.setItem('custom_units_list', JSON.stringify(updated));
                setNewCustomUnit('');
                alert('已新增機構，請重新整理網頁生效');
            };
            const handleRemoveCustomUnit = (u) => {
                const updated = customUnits.filter(x => x !== u);
                setCustomUnits(updated);
                localStorage.setItem('custom_units_list', JSON.stringify(updated));
            };
"""
content = content.replace(admin_panel_start, admin_panel_new)

# 7. Add UI for managing Custom Units in Admin Panel
admin_ui_find = """                                <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm flex flex-col gap-6">
                                    <div>
                                        <h3 className="font-bold text-slate-800 mb-4 flex items-center gap-2">?? 系統備份與還原</h3>"""

admin_ui_new = """                                <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm flex flex-col gap-6">
                                    <div>
                                        <h3 className="font-bold text-slate-800 mb-4 flex items-center gap-2">?? 機構(單位)擴充管理</h3>
                                        <div className="flex gap-2 mb-4">
                                            <input type="text" value={newCustomUnit} onChange={e => setNewCustomUnit(e.target.value)} placeholder="輸入新機構名稱..." className="flex-1 p-2 border rounded-lg text-sm" />
                                            <button onClick={handleAddCustomUnit} className="bg-blue-600 text-white px-3 rounded-lg text-sm font-bold">新增</button>
                                        </div>
                                        <div className="space-y-2">
                                            {customUnits.map(u => (
                                                <div key={u} className="flex justify-between items-center bg-slate-50 p-2 rounded border">
                                                    <span className="text-sm">{u}</span>
                                                    <button onClick={() => handleRemoveCustomUnit(u)} className="text-red-500 text-xs font-bold px-2 py-1 bg-red-100 rounded">刪除</button>
                                                </div>
                                            ))}
                                            {customUnits.length === 0 && <div className="text-xs text-slate-400 text-center">目前無自訂擴充機構</div>}
                                        </div>
                                    </div>
                                </div>

                                <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm flex flex-col gap-6">
                                    <div>
                                        <h3 className="font-bold text-slate-800 mb-4 flex items-center gap-2">?? 系統備份與還原</h3>"""
content = content.replace(admin_ui_find, admin_ui_new)

# 8. Update ALL_UNITS to dynamicUnits in AdminPanel dropdown
content = content.replace("""{ALL_UNITS.map(u => <option key={u} value={u}>{u}</option>)}""", """{[...new Set([...ALL_UNITS, ...(JSON.parse(localStorage.getItem('custom_units_list') || '[]'))])].map(u => <option key={u} value={u}>{u}</option>)}""")

# 9. Replace hardcoded options block with dynamicUnits map
# We will use regex to find all <select> blocks and replace the <option value="清福養老院">... block.
# We will just replace ALL instances of `<option value="清福養老院">...<option value="清福護理之家">清福護理之家</option>` with `<DynamicOptions/>` text, and define it, or just inject `{dynamicUnits.filter(u=>u!=='生福課').map(...)`
regex_options = r'<option value="清福養老院">清福養老院</option>[\s\S]*?<option value="清福護理之家">清福護理之家</option>'
content = re.sub(regex_options, "{dynamicUnits.filter(u => u !== '生福課').map(u => <option key={u} value={u}>{u}</option>)}", content)

# 10. Update filter list (it has "生福課" excluded usually, but in filter it includes all except 生福課)
regex_options2 = r'<option value="清福一館">清福一館</option>[\s\S]*?<option value="清福護理之家">清福護理之家</option>'
content = re.sub(regex_options2, "{dynamicUnits.filter(u => u !== '生福課').map(u => <option key={u} value={u}>{u}</option>)}", content)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(content)

print("Refactor complete")
