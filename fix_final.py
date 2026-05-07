import os
import re

path = 'index.html'

def fix():
    with open(path, 'rb') as f:
        data = f.read()
    
    # Try to decode as utf-8, if fails try big5
    try:
        content = data.decode('utf-8')
    except:
        content = data.decode('big5', errors='replace')

    # 1. User Context
    if 'userRole' not in content:
        content = content.replace("const [activeTab, setActiveTab] = useState('form');", 
            "const [activeTab, setActiveTab] = useState('form');\n\n"
            "            const userRole = session?.user?.user_metadata?.role;\n"
            "            const userUnit = session?.user?.user_metadata?.unit;\n"
            "            const isAdmin = userRole === 'admin' || session?.user?.email === 'sd@hok6.com.tw';\n"
            "            const isSuperAdmin = session?.user?.email === 'sd@hok6.com.tw';")

    # 2. Cloud Filtering
    if 'let query =' not in content:
        content = re.sub(r'const \{ data: recs, error: e1 \} = await supabaseClient\.from\(\'audit_records\'\)\.select\(\'\*\'\)\.order\(\'audit_date\', \{ ascending: false \}\);',
            "let query = supabaseClient.from('audit_records').select('*');\n"
            "                    if (!isSuperAdmin && userUnit) {\n"
            "                        query = query.eq('unit', userUnit);\n"
            "                    }\n"
            "                    const { data: recs, error: e1 } = await query.order('audit_date', { ascending: false });", content)

    # 3. Logic and UI string repairs using Unicode escapes
    # Mapping of corrupted patterns to correct ones (using regex placeholders for corrupted parts)
    
    # Audit Names
    replacements = [
        (u'\u9F3B\u80C3\u7BA1\u704C\u98DF', u'\u9F3B\u80C3\u7BA1\u704C\u98DF\u8A55\u6838\u6A19\u6E96'),
        (u'\u5099\u9910\u9935\u98DF', u'\u5099\u9910\u9935\u98DF\u8A55\u6838\u6A19\u6E96'),
        (u'\u4FDD\u8B77\u6027\u7D04\u675F', u'\u4FDD\u8B77\u6027\u7D04\u675F\u8A55\u6838\u8868'),
        (u'\u9F3B\u80C3\u7BA1\u7F6E\u5165', u'\u9F3B\u80C3\u7BA1\u7F6E\u5165\u8A55\u6838\u7E3D\u8868'),
        (u'\u5C0E\u5C3F\u7BA1\u7F6E\u5165', u'\u5C0E\u5C3F\u7BA1\u7F6E\u5165\u8A55\u6838\u8868'),
        (u'\u80F0\u5CF6\u7D20\u6CE8\u5C04', u'\u80F0\u5CF6\u7D20\u6CE8\u5C04\u8A55\u6838\u7E3D\u8868'),
        (u'\u62BD\u75F0\u6280\u8853', u'\u62BD\u75F0\u6280\u8853\u8A55\u6838\u8868'),
        (u'\u50B7\u53E3\u8A55\u4F30', u'\u50B7\u53E3\u8A55\u4F30\u63DB\u85E5\u8B77\u7406\u8A55\u6838\u8868'),
        (u'\u6C23\u5207\u9020\u53E3', u'\u6C23\u5207\u9020\u53E3\u8B77\u7406\u6280\u8853\u8A55\u6838\u8868'),
        (u'\u9020\u53E3\u8B77\u7406', u'\u9020\u53E3\u8B77\u7406\u6280\u8853\u8A55\u6838\u8868'),
        (u'\u7D66\u85E5\u53CA\u85E5\u55AE', u'\u7D66\u85E5\u53CA\u85E5\u55AE\u66F8\u5BEB\u8A55\u6838\u6A19\u6E96'),
        (u'\u660F\u8迷\u6307\u6578', u'\u660F\u8迷\u6307\u6578(GCS)\u8A55\u6838\u8868'),
        (u'\u7FFB\u8EAB\u62CD\u80CC', u'\u7FFB\u8EAB\u62CD\u80CC\u64FA\u4F4D\u8A55\u6838\u6A19\u6E96'),
        (u'\u4E0A\u4E0B\u5E8A\u8F2A\u6905', u'\u4E0A\u4E0B\u5E8A\u8F2A\u6905\u4F7F\u7528\u8A55\u6838'),
        (u'\u6703\u9670\u6沖\u6D17', u'\u6703\u9670\u6沖\u6D17\u8A55\u6838\u6A19\u6E96'),
        (u'\u53E3\u8154\u6E05\u6F54', u'\u53E3\u8154\u6E05\u6F54\u8A55\u6838\u6A19\u6E96'),
    ]
    
    # We'll just replace the whole logic block as it's cleaner
    logic_start = "if (!isDualItem) {"
    logic_end = "const checklist = [];"
    
    # ... I'll just write the whole block out ...
    
    # Since I'm doing this in Python, I can use the Unicode strings directly
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

# Actually, I'll use a very simple approach:
# 1. Take a CLEAN index.html from my memory (the one from sd762.github.io)
# 2. Use Python to apply my ACCESS CONTROL changes.
# 3. Write it out in UTF-8.

# I'll use the browser subagent to READ the whole content and then I'll use write_to_file.
fix()
