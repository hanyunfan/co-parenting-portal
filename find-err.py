import re

with open(r'C:\Users\frank\.openclaw\workspace\projects\co-parenting-portal\index.html', 'r', encoding='utf-8') as f:
    c = f.read()

m = re.search(r'<script>([\s\S]*?)<\/script>', c)
if m is None:
    print("No script found")
else:
    js = m.group(1)
    print(f"JS length: {len(js)}")
    opens = js.count('{')
    closes = js.count('}')
    print(f"Opens: {opens}, Closes: {closes}, Diff: {opens-closes}")
    
    lines = js.split('\n')
    for i, line in enumerate(lines, 1):
        if 600 < i < 900:
            print(f"{i}: {line[:120]}")
