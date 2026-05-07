import re

with open("index.html", "r", encoding="utf-8") as f:
    text = f.read()

script = re.search(r'<script type="text/babel">(.*?)</script>', text, re.DOTALL)
if script:
    code = script.group(1)
    # Check for basic bracket matching (ignoring strings/regex for simplicity)
    # This might have false positives if brackets are in strings, but good for a quick check
    stack = []
    lines = code.split('\n')
    for i, line in enumerate(lines):
        in_string = False
        quote_char = None
        for char in line:
            if char in ("'", '"', '`'):
                if not in_string:
                    in_string = True
                    quote_char = char
                elif quote_char == char:
                    in_string = False
            if in_string:
                continue
                
            if char in '{[(':
                stack.append((char, i+1))
            elif char in '}])':
                if not stack:
                    print(f'Unmatched closing {char} on line {i+1}')
                else:
                    last, _ = stack.pop()
                    if (char == '}' and last != '{') or \
                       (char == ']' and last != '[') or \
                       (char == ')' and last != '('):
                        print(f'Mismatched closing {char} on line {i+1}')
    if stack:
        print(f'Unmatched opening brackets: {stack}')
    else:
        print('All brackets match perfectly.')
