import re

with open("index.html", "r", encoding="utf-8-sig") as f:
    content = f.read()

# Replace optgroup block
opt_group_block = """                                                <optgroup label="法人館"><option value="清福一館">清福一館</option><option value="清福二館">清福二館</option><option value="清福三館">清福三館</option></optgroup>
                                                <optgroup label="養護機構">
                                                    <option value="清福養老院">清福養老院</option><option value="清春養老院">清春養老院</option><option value="清山養老院">清山養老院</option>
                                                    <option value="清氣養老院">清氣養老院</option><option value="清日養老院">清日養老院</option><option value="清泉養老院">清泉養老院</option>
                                                    <option value="清心養老院">清心養老院</option><option value="清照養老院">清照養老院</option><option value="清水養老院">清水養老院</option>
                                                    <option value="清平養老院">清平養老院</option><option value="清風養老院">清風養老院</option><option value="清清養老院">清清養老院</option>
                                                    <option value="清安養老院">清安養老院</option><option value="清景養老院">清景養老院</option><option value="清涼養老院">清涼養老院</option>
                                                </optgroup>
                                                <optgroup label="護理之家"><option value="清福護理之家">清福護理之家</option></optgroup>"""

dynamic_options = "{dynamicUnits.filter(u => u !== '生福課').map(u => <option key={u} value={u}>{u}</option>)}"
content = content.replace(opt_group_block, dynamic_options)

# Replace other block with <option value="清福一館"> ... <option value="清福護理之家">
block_2 = """                                                            <option value="清福一館">清福一館</option>
                                                            <option value="清福二館">清福二館</option>
                                                            <option value="清福三館">清福三館</option>
                                                            <option value="清福養老院">清福養老院</option>
                                                            <option value="清春養老院">清春養老院</option>
                                                            <option value="清山養老院">清山養老院</option>
                                                            <option value="清氣養老院">清氣養老院</option>
                                                            <option value="清日養老院">清日養老院</option>
                                                            <option value="清泉養老院">清泉養老院</option>
                                                            <option value="清心養老院">清心養老院</option>
                                                            <option value="清照養老院">清照養老院</option>
                                                            <option value="清水養老院">清水養老院</option>
                                                            <option value="清平養老院">清平養老院</option>
                                                            <option value="清風養老院">清風養老院</option>
                                                            <option value="清清養老院">清清養老院</option>
                                                            <option value="清安養老院">清安養老院</option>
                                                            <option value="清景養老院">清景養老院</option>
                                                            <option value="清涼養老院">清涼養老院</option>
                                                            <option value="清福護理之家">清福護理之家</option>"""
content = content.replace(block_2, dynamic_options)

# Replace block with <option value="清福養老院"> ...
block_3 = """                                                            <option value="清福養老院">清福養老院</option>
                                                            <option value="清春養老院">清春養老院</option>
                                                            <option value="清山養老院">清山養老院</option>
                                                            <option value="清氣養老院">清氣養老院</option>
                                                            <option value="清日養老院">清日養老院</option>
                                                            <option value="清泉養老院">清泉養老院</option>
                                                            <option value="清心養老院">清心養老院</option>
                                                            <option value="清照養老院">清照養老院</option>
                                                            <option value="清水養老院">清水養老院</option>
                                                            <option value="清平養老院">清平養老院</option>
                                                            <option value="清風養老院">清風養老院</option>
                                                            <option value="清清養老院">清清養老院</option>
                                                            <option value="清安養老院">清安養老院</option>
                                                            <option value="清景養老院">清景養老院</option>
                                                            <option value="清涼養老院">清涼養老院</option>
                                                            <option value="清福護理之家">清福護理之家</option>"""
content = content.replace(block_3, dynamic_options)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
