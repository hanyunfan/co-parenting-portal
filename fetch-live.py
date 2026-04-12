import urllib.request, re

url = 'https://hanyunfan.github.io/co-parenting-portal/'
with urllib.request.urlopen(url, timeout=15) as r:
    html = r.read().decode('utf-8', errors='replace')

print(f"HTML len: {len(html)}")

m = re.search(r'<script>([\s\S]*?)</script>', html)
if not m:
    print("No script")
else:
    js = m.group(1)
    print(f"JS len: {len(js)}")
    print(f"Has isMomSummerDay: {'isMomSummerDay' in js}")
    print(f"Has generateESPOCalendar: {'generateESPOCalendar' in js}")

    tmp = 'C:/Users/frank/.openclaw/workspace/projects/co-parenting-portal/_tmp_live.js'
    with open(tmp, 'w', encoding='utf-8') as f:
        f.write(js)

import subprocess, os
r = subprocess.run(['node', '--check', tmp], capture_output=True, text=True)
print(f"JS syntax: {'OK' if r.returncode == 0 else 'FAIL'}")
if r.returncode != 0:
    print(r.stderr[:500])
os.remove(tmp)
