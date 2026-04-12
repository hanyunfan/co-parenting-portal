import re

with open(r'C:\Users\frank\.openclaw\workspace\projects\co-parenting-portal\index.html', 'r', encoding='utf-8') as f:
    c = f.read()

lines = c.split('\n')
for i, line in enumerate(lines, 1):
    if 850 < i < 890:
        print(f"{i}: {line}")
