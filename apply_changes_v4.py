import os
import re

path = 'index.html'

def apply_changes():
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. State Variables & Modals
    if 'const userRole =' not in content:
        state_injection = """const [activeTab, setActiveTab] = useState('form');
            const [showPwdModal, setShowPwdModal] = useState(false);
            const [newPwd, setNewPwd] = useState('');
            const [pwdError, setPwdError] = useState('');
            const [pwdMsg, setPwdMsg] = useState('');
            
            const userRole = session?.user?.user_metadata?.role;
            const userUnit = session?.user?.user_metadata?.unit;
            const isAdmin = userRole === 'admin' || session?.user?.email === 'sd@hok6.com.tw';
            const isSuperAdmin = session?.user?.email === 'sd@hok6.com.tw';
            const displayRole = isSuperAdmin ? '系統開發者' : (isAdmin ? '系統管理員' : '機構帳號');"""
        content = content.replace("const [activeTab, setActiveTab] = useState('form');", state_injection)

    # 2. Cloud Data Isolation
    cloud_isolation = """let query = supabaseClient.from('audit_records').select('*');
                    if (!isSuperAdmin && userUnit) {
                        query = query.eq('unit', userUnit);
                    }
                    const { data: recs, error: e1 } = await query.order('audit_date', { ascending: false });"""
    content = re.sub(r"const \{\s*data:\s*recs,\s*error:\s*e1\s*\}\s*=\s*await\s*supabaseClient\.from\('audit_records'\)\.select\('\*'\)\.order\('audit_date',\s*\{\s*ascending:\s*false\s*\}\);", cloud_isolation, content)

    # 3. Report Data Filtering
    report_filter = """const baseFilter = String(r.date).startsWith(selectedYear) && r.auditName.includes(tpl.name);
                        if (!isSuperAdmin && userUnit) {
                            return baseFilter && r.unit === userUnit;
                        }
                        return baseFilter && (filterUnit ? r.unit === filterUnit : (filterUnitCategory ? uCat === filterUnitCategory : true));"""
    content = re.sub(r"return\s*String\(r\.date\)\.startsWith\(selectedYear\)\s*&&\s*r\.auditName\.includes\(tpl\.name\)\s*&&\s*\(filterUnit\s*\?\s*r\.unit\s*===\s*filterUnit\s*:\s*\(filterUnitCategory\s*\?\s*uCat\s*===\s*filterUnitCategory\s*:\s*true\)\);", report_filter, content)

    # 4. Local Record Filtering
    content = content.replace("const isUnitMatch = userUnit ? r.unit === userUnit", "const isUnitMatch = (!isSuperAdmin && userUnit) ? r.unit === userUnit")
    content = content.replace("}, [records, filterMonth, filterItem, filterUnitCategory, filterUnit, userUnit]);", "}, [records, filterMonth, filterItem, filterUnitCategory, filterUnit, userUnit, isSuperAdmin]);")

    # 5. UI Elements
    # Navigation Bar (Status + Change Password)
    nav_old = """<div className="flex flex-col"><h1 className="font-bold text-lg tracking-tight">清福技術考稽核系統</h1><span className="text-[9px] bg-white/20 px-2 py-0.5 rounded self-start uppercase">V1.3 彈性擴充版</span></div>
                        <div className="flex items-center gap-3">"""
    nav_new = """<div className="flex flex-col"><h1 className="font-bold text-lg tracking-tight">清福技術考稽核系統</h1><span className="text-[9px] bg-white/20 px-2 py-0.5 rounded self-start uppercase">V1.3 彈性擴充版</span></div>
                        
                        {session && (
                            <div className="hidden md:flex items-center gap-2 bg-white/10 px-3 py-1.5 rounded-lg text-xs">
                                <span className="font-bold">{userUnit ? `[${userUnit}]` : ''}</span>
                                <span>{session.user.email}</span>
                                <span className="bg-primary-dark px-1.5 py-0.5 rounded text-[10px] uppercase border border-white/20">{displayRole}</span>
                            </div>
                        )}

                        <div className="flex items-center gap-3">
                            <button onClick={() => setShowPwdModal(true)} className="bg-white/10 hover:bg-white/20 text-white text-xs px-3 py-1.5 rounded font-bold transition-colors">
                                變更密碼
                            </button>"""
    content = content.replace(nav_old, nav_new)

    # Form Tab Locks
    content = content.replace('<select value={formData.unitCategory} onChange={e => {', '<select value={formData.unitCategory} disabled={!isSuperAdmin && !!userUnit} onChange={e => {')
    content = re.sub(r'<select value=\{formData\.unit\}\s*onChange=\{e => setFormData\(\{ \.\.\.formData, unit: e\.target\.value \}\)\}\s*className="flex-1 p-2 border border-slate-200 rounded text-sm outline-none bg-white">', '<select value={formData.unit} disabled={!isSuperAdmin && !!userUnit} onChange={e => setFormData({ ...formData, unit: e.target.value })} className="flex-1 p-2 border border-slate-200 rounded text-sm outline-none bg-white disabled:bg-slate-50 disabled:text-slate-500">', content)

    # History Tab Locks
    history_filter_hide = """{(!userUnit || isSuperAdmin) && (<>"""
    content = content.replace('<select value={filterUnitCategory}', history_filter_hide + '\n<select value={filterUnitCategory}')
    # We find the end of the history select area. It is before `<button onClick={exportToExcel}`
    # Since regex can be tricky, I'll insert `</>)}` before `<button onClick={exportToExcel}`
    # Actually, the History and Chart tabs both have exportToExcel, so I'll find specific lines.
    
    # Simpler: replace `<select value={filterUnit}`... `</select>` with conditional.
    # Wait, there are two `filterUnitCategory` selects. One in history, one in chart.
    # I'll replace all `<select value={filterUnitCategory}` with `{(!userUnit || isSuperAdmin) && <select value={filterUnitCategory}`
    # And their corresponding closing tags or following siblings.
    
    # Since python replacement is exact, let's just do:
    content = content.replace('<select value={filterUnitCategory} onChange={e =>', '{(!userUnit || isSuperAdmin) && <select value={filterUnitCategory} onChange={e =>')
    content = content.replace('<select value={filterUnit} onChange={e => setFilterUnit', '{(!userUnit || isSuperAdmin) && <select value={filterUnit} onChange={e => setFilterUnit')
    content = content.replace('</select>\n                                </div>\n                            </div>\n                        </div>\n                    )}', '</select>}\n                                </div>\n                            </div>\n                        </div>\n                    )}')
    # Let's fix the closing tags precisely:
    content = content.replace('</select>\n                                    <button onClick={exportToExcel}', '</select>}\n                                    <button onClick={exportToExcel}')
    content = content.replace('</select>\n                                </div>\n\n                                {loadingAuth', '</select>}\n                                </div>\n\n                                {loadingAuth')


    # Admin Tab Protection
    content = content.replace("<button onClick={() => setActiveTab('admin')}", "{isAdmin && <button onClick={() => setActiveTab('admin')}")
    content = content.replace("<IconAdmin /> 系統後台</button>", "<IconAdmin /> 系統後台</button>}")
    
    # Password Modal Injection
    pwd_modal = """
                    {showPwdModal && (
                        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-slate-900/40 backdrop-blur-sm p-4 animate-fade-in">
                            <div className="bg-white rounded-2xl w-full max-w-sm shadow-2xl p-6">
                                <h3 className="font-bold text-lg mb-4">變更密碼</h3>
                                <div className="space-y-4">
                                    <input 
                                        type="password" 
                                        placeholder="輸入新密碼 (至少 6 碼)" 
                                        value={newPwd} 
                                        onChange={e => setNewPwd(e.target.value)} 
                                        className="w-full p-2 border rounded outline-none focus:border-primary"
                                    />
                                    {pwdError && <p className="text-red-500 text-xs">{pwdError}</p>}
                                    {pwdMsg && <p className="text-green-600 text-xs">{pwdMsg}</p>}
                                    <div className="flex gap-2 justify-end mt-4">
                                        <button onClick={() => setShowPwdModal(false)} className="px-4 py-2 bg-slate-100 rounded-lg text-sm font-bold">取消</button>
                                        <button onClick={async () => {
                                            if (newPwd.length < 6) { setPwdError('密碼長度至少需要 6 碼'); return; }
                                            setPwdError(''); setPwdMsg('');
                                            const { error } = await supabaseClient.auth.updateUser({ password: newPwd });
                                            if (error) setPwdError(error.message);
                                            else {
                                                setPwdMsg('密碼變更成功！即將關閉...');
                                                setTimeout(() => { setShowPwdModal(false); setNewPwd(''); setPwdMsg(''); }, 1500);
                                            }
                                        }} className="px-4 py-2 bg-primary text-white rounded-lg text-sm font-bold shadow">確認變更</button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}
    """
    
    # Inject pwd_modal before the final dialog modal
    content = content.replace('{dialog.isOpen && (', pwd_modal + '\n                    {dialog.isOpen && (')

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

apply_changes()
