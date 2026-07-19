import re
lines = open('routes_diff.txt', encoding='utf-8').readlines()
clean_lines = []
parsing = False
for l in lines:
    if l.startswith('1: '):
        parsing = True
    if parsing:
        m = re.match(r'^\d+:\s?(.*)', l)
        if m:
            clean_lines.append(m.group(1)+'\n')
        else:
            if not l.startswith('The above content') and not l.startswith('The following code'):
                clean_lines.append(l)
open('backend/api/routes.py', 'w', encoding='utf-8').writelines(clean_lines)
