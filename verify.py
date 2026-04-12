import re

with open('C:/Users/frank/.openclaw/workspace/projects/co-parenting-portal/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

print(f"File size: {len(c)}")

# Check getSchoolBreakCustody
print('\n=== getSchoolBreakCustody ===')
idx = c.find('function getSchoolBreakCustody')
if idx >= 0: print(c[idx:idx+700])
else: print('NOT FOUND')

# Check isMomSummerDay
print('\n=== isMomSummerDay ===')
idx = c.find('function isMomSummerDay')
if idx >= 0: print(c[idx:idx+300])
else: print('NOT FOUND')

# Check endMonth
print('\n=== Calendar bounds ===')
for m in re.finditer(r'endYear\s*=\s*(\d+)\s*,\s*endMonth\s*=\s*(\d+)', c):
    print(f'  endYear={m.group(1)}, endMonth={m.group(2)} at {m.start()}')

# Check isSummerBreak count
count = c.count("const isSummerBreak")
print(f'\nisSummerBreak count: {count}')

# Check isMomSummerDay usage
print('\n=== isMomSummerDay usage in day loop ===')
idx = c.find("isMomSummerDay_val")
if idx >= 0:
    print(c[idx-20:idx+500])
else:
    print("NOT FOUND in day loop")

# Check breakCustody usage
print('\n=== breakCustody usage ===')
idx = c.find("breakCustody")
if idx >= 0:
    print(c[idx-20:idx+400])
else:
    print("NOT FOUND")
