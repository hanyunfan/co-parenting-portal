with open(r'C:\Users\frank\.openclaw\workspace\projects\co-parenting-portal\index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Line 797 (index 796) has a dangling string
print(repr(lines[796]))
print(repr(lines[797]))
print(repr(lines[798]))
