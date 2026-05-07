import os
import re

path = 'index.html'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Fix finalAuditName logic
new_logic = """                                    if (cleanRaw.includes('鼻胃管灌食')) finalAuditName = '鼻胃管灌食評核標準';
                                    else if (cleanRaw.includes('備餐餵食') || cleanRaw.includes('備餐')) finalAuditName = '備餐餵食評核標準';
                                    else if (cleanRaw.includes('保護性約束') || cleanRaw.includes('約束')) finalAuditName = '保護性約束評核表';
                                    else if (cleanRaw.includes('鼻胃管置入')) finalAuditName = '鼻胃管置入評核總表';
                                    else if (cleanRaw.includes('導尿管置入') || cleanRaw.includes('導尿管')) finalAuditName = '導尿管置入評核表';
                                    else if (cleanRaw.includes('胰島素注射') || cleanRaw.includes('胰島素')) finalAuditName = '胰島素注射評核總表';
                                    else if (cleanRaw.includes('抽痰技術') || cleanRaw.includes('抽痰')) finalAuditName = '抽痰技術評核表';
                                    else if (cleanRaw.includes('傷口評估') || cleanRaw.includes('換藥')) finalAuditName = '傷口評估換藥護理評核表';
                                    else if (cleanRaw.includes('氣切造口') || cleanRaw.includes('氣切')) finalAuditName = '氣切造口護理技術評核表';
                                    else if (cleanRaw.includes('造口護理')) finalAuditName = '造口護理技術評核表';
                                    else if (cleanRaw.includes('給藥及藥單') || cleanRaw.includes('給藥')) finalAuditName = '給藥及藥單書寫評核標準';
                                    else if (cleanRaw.includes('昏迷指數') || cleanRaw.includes('GCS')) finalAuditName = '昏迷指數(GCS)評核表';
                                    else if (cleanRaw.includes('翻身拍背') || cleanRaw.includes('翻身')) finalAuditName = '翻身拍背擺位評核標準';
                                    else if (cleanRaw.includes('上下床輪椅') || cleanRaw.includes('上下床') || cleanRaw.includes('輪椅')) finalAuditName = '上下床輪椅使用評核';
                                    else if (cleanRaw.includes('會陰沖洗') || cleanRaw.includes('會陰')) finalAuditName = '會陰沖洗評核標準';
                                    else if (cleanRaw.includes('口腔清潔') || cleanRaw.includes('口腔')) finalAuditName = '口腔清潔評核標準';"""

content = re.sub(r'if \(cleanRaw\.includes\(\'[^\']+\'\)\) finalAuditName = \'[^\']+\';.*?\n\s+else \{', new_logic + "\n                                    else {", content, flags=re.DOTALL)

# 2. Fix stripTerms
new_strip = "const stripTerms = (n) => n.replace(/(評核標準|評核表|評核總表|技術評核表|護理技術評核表|使用評核|擺位評核標準|書寫評核標準)/g, '');"
content = re.sub(r'const stripTerms = \(n\) => n\.replace\(.*?, \'\'\);', new_strip, content)

# 3. Fix unitCategory strings (using regex for corrupted patterns)
content = content.replace('?????????', '清福養老院系列')
content = content.replace('?????', '清福體系')
content = content.replace('??風??', '清福一村')
content = content.replace('???€??', '清福養老院')
content = content.replace('?????', '清春養老院')
content = content.replace('?????', '清泰養老院')

# 4. Fix other common UI strings
content = content.replace('?絞敺?', '系統後台管理')
# content = content.replace('脤?{selectedIds.size} ??', '已選取 {selectedIds.size} 筆') # This is risky

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Fixed corruption successfully.")
