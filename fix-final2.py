with open('C:/Users/frank/.openclaw/workspace/projects/co-parenting-portal/index.html', 'rb') as f:
    raw = f.read()
c = raw.decode('utf-8')

print(f"File size: {len(c)}")

# Find calendar bounds - be flexible with whitespace
import re
m = re.search(r'const\s+startYear\s*=\s*2026\s*,\s*startMonth\s*=\s*3\s*;\s*const\s+endYear\s*=\s*2027\s*,\s*endMonth\s*=\s*(\d+)', c)
if m:
    print(f"Current endMonth: {m.group(1)}")
    # Replace with 7
    c = re.sub(r'const\s+startYear\s*=\s*2026\s*,\s*startMonth\s*=\s*3\s*;\s*const\s+endYear\s*=\s*2027\s*,\s*endMonth\s*=\s*\d+',
               'const startYear = 2026, startMonth = 3; const endYear = 2027, endMonth = 7;',
               c, count=2)
    print("1. Calendar bounds extended (SPO and ESPO) OK")
else:
    print("1. Calendar bounds not found")

# Verify no duplicate const isSummerBreak in SPO
count = c.count("const isSummerBreak = breakInfo")
print(f"const isSummerBreak count: {count}")

# Find the SPO function and remove the duplicate
spo_func = c.find("function generateSPOCalendar")
esp_func = c.find("function generateESPOCalendar")
spo_section = c[spo_func:esp_func]

# In SPO function, count occurrences of isSummerBreak
spo_summer_count = spo_section.count("const isSummerBreak = breakInfo")
print(f"SPO function isSummerBreak count: {spo_summer_count}")

if spo_summer_count > 1:
    # Find and remove the duplicate one
    # Look for the comment that's duplicated
    idx1 = spo_section.find("const isSummerBreak = breakInfo")
    idx2 = spo_section.find("const isSummerBreak = breakInfo", idx1 + 1)
    if idx2 > 0:
        # Remove from idx2 to end of that line
        end_idx = spo_section.find("\n", idx2)
        to_remove = spo_section[idx2:end_idx+1]
        c = c[:spo_func + idx2] + c[spo_func + end_idx + 1:]
        print(f"Removed duplicate isSummerBreak from SPO")
    else:
        print("Could not find duplicate location")

# Now verify
count = c.count("const isSummerBreak = breakInfo")
print(f"After fix, isSummerBreak count: {count}")

# Update extendedDad HTML text - find and replace
old_html = '<p id="extendedDad">Father: 1st, 3rd, 5th week Thu after school - Sun 6 PM + 30 days summer; plus every Thu 6-8 PM on weeks 2 &amp; 4</p>'
if old_html in c:
    new_html = '<p id="extendedDad">Father: 1st/3rd/5th week Thu after school-Sun 6PM (+ Mon AM if school off) + 30 consecutive days in summer (Jul 1-30, default); weeks 2 &amp; 4: every Thu after school (standard SPO). Mother: spring/winter break first half; summer remaining days (Jul 31 + Aug 1-2).</p>'
    c = c.replace(old_html, new_html)
    print("extendedDad HTML updated OK")
else:
    # Try without &amp;
    old_html2 = re.sub(r'&amp;', '&', old_html)
    if old_html2 in c:
        new_html = '<p id="extendedDad">Father: 1st/3rd/5th week Thu after school-Sun 6PM (+ Mon AM if school off) + 30 consecutive days in summer (Jul 1-30, default); weeks 2 &amp; 4: every Thu after school (standard SPO). Mother: spring/winter break first half; summer remaining days (Jul 31 + Aug 1-2).</p>'
        c = c.replace(old_html2, new_html)
        print("extendedDad HTML updated OK (no &amp;)")
    else:
        # Find what's actually there
        match = re.search(r'<p id="extendedDad">[^<]+</p>', c)
        if match:
            print(f"Found extendedDad HTML: {repr(match.group()[:100])}")
        else:
            print("extendedDad HTML NOT FOUND")

# Update CN extendedDad in i18n
old_cn = "extendedDad: '父亲：每月第1、3、5周周四放学后至周日6点（+周一早上如果学校不上课）+ 夏季30天；第2、4周：每周四下午6点至8点（标准SPO）',"
if old_cn in c:
    new_cn = "extendedDad: '父亲：每月第1/3/5周周四放学后至周日6点（+周一早上如果学校不上课）+ 夏季30天（默认7月1-30日）；第2/4周：每周四放学后（标准SPO）。母亲：春假/寒假前半段；暑假剩余天数（7月31日+8月1-2日）。',"
    c = c.replace(old_cn, new_cn)
    print("extendedDad CN updated OK")
else:
    print("extendedDad CN NOT FOUND, trying flexible match")
    m2 = re.search(r"extendedDad:\s*'父亲：[^']+'", c)
    if m2:
        print(f"Found CN: {repr(m2.group()[:100])}")

with open('C:/Users/frank/.openclaw/workspace/projects/co-parenting-portal/index.html', 'w', encoding='utf-8', newline='\n') as f:
    f.write(c)
print("Done!")
