with open('C:/Users/frank/.openclaw/workspace/projects/co-parenting-portal/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

# Find schoolBreaks
idx = c.find('schoolBreaks = ')
end = c.find('];', idx)
sb = c[idx:end+2]
print(sb)
