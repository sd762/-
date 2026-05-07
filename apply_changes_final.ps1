$path = 'index.html'
$c = [System.IO.File]::ReadAllText($path, [System.Text.Encoding]::UTF8)

# 1. User Context (App component)
$c = $c -replace 'const \[activeTab, setActiveTab\] = useState\(''form''\);', 'const [activeTab, setActiveTab] = useState(''form'');' + "`n`n            const userRole = session?.user?.user_metadata?.role;`n            const userUnit = session?.user?.user_metadata?.unit;`n            const isAdmin = userRole === ''admin'' || session?.user?.email === ''sd@hok6.com.tw'';`n            const isSuperAdmin = session?.user?.email === ''sd@hok6.com.tw'';"

# 2. Cloud Data Filtering (loadAllDataFromCloud)
$c = $c -replace '(?s)const \{ data: recs, error: e1 \} = await supabaseClient\.from\(''audit_records''\)\.select\(''\*''\)\.order\(''audit_date'', \{ ascending: false \}\);', "let query = supabaseClient.from('audit_records').select('*');`n                    if (!isSuperAdmin && userUnit) {`n                        query = query.eq('unit', userUnit);`n                    }`n                    const { data: recs, error: e1 } = await query.order('audit_date', { ascending: false });"

# 3. Report Data Filtering (buildTableData)
# This one is tricky due to multiple lines and potentially duplicate patterns.
# I'll use a more specific regex.
$c = $c -replace '(?s)return String\(r\.date\)\.startsWith\(selectedYear\) &&\s+r\.auditName\.includes\(tpl\.name\) &&\s+\(filterUnit \? r\.unit === filterUnit : \(filterUnitCategory \? uCat === filterUnitCategory : true\)\);', "const baseFilter = String(r.date).startsWith(selectedYear) && r.auditName.includes(tpl.name);`n                        if (!isSuperAdmin && userUnit) {`n                            return baseFilter && r.unit === userUnit;`n                        }`n                        return baseFilter && (filterUnit ? r.unit === filterUnit : (filterUnitCategory ? uCat === filterUnitCategory : true));"

# 4. Local Record Filtering (flatFilteredRecords)
$c = $c -replace 'const isUnitMatch = userUnit \? r\.unit === userUnit', 'const isUnitMatch = (!isSuperAdmin && userUnit) ? r.unit === userUnit'
$c = $c -replace '\}, \[records, filterMonth, filterItem, filterUnitCategory, filterUnit, userUnit\]\);', '}, [records, filterMonth, filterItem, filterUnitCategory, filterUnit, userUnit, isSuperAdmin]);'

# 5. Form Tab Unit Selection Locking
$c = $c -replace '<select value=\{formData\.unitCategory\} onChange=\{e => \{', '<select value={formData.unitCategory} disabled={!isSuperAdmin && !!userUnit} onChange={e => {'
$c = $c -replace '<select value=\{formData\.unit\} onChange=\{e => setFormData\(.*?\) className="flex-1 p-2 border border-slate-200 rounded text-sm outline-none bg-white">', '$0'
# Wait! I'll just use a simpler replacement for the className
$c = $c -replace 'className="flex-1 p-2 border border-slate-200 rounded text-sm outline-none bg-white"', 'className="flex-1 p-2 border border-slate-200 rounded text-sm outline-none bg-white disabled:bg-slate-50 disabled:text-slate-500"'

# 6. History/Chart Filters Hiding
$c = $c -replace '(<select value=\{filterItem\}.*?<\/select>)', '$1' + "`n`n                                    {(!userUnit || isSuperAdmin) && (<>"
# Closing tag for History (using landmark)
$c = $c -replace '(?s)(\{!\(!userUnit \|\| isSuperAdmin\) && \(<>\}.*?<\/select>\s*)\)\}\s+<span', '$1</>)}' + "`n`n                                    <span"
# Closing tag for Chart (using landmark)
$c = $c -replace '(?s)(\{!\(!userUnit \|\| isSuperAdmin\) && \(<>\}.*?<\/select>\s*)\r?\n\s+<\/div>', '$1</>)}' + "`n                                </div>"

# 7. Admin Tab Protection
$c = $c -replace '(?s)(<button onClick=\{\(\) => setActiveTab\(''admin''\)\}.*?<\/button>)', '{isAdmin && $1}'

[System.IO.File]::WriteAllText($path, $c, [System.Text.Encoding]::UTF8)
