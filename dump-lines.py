with open(r'C:\Users\frank\.openclaw\workspace\projects\co-parenting-portal\index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

with open(r'C:\Users\frank\.openclaw\workspace\projects\co-parenting-portal\dump.txt', 'w', encoding='utf-8') as f:
    for i, line in enumerate(lines, 1):
        if 855 < i < 890:
            f.write(f"{i}: {line.rstrip()}\n")
