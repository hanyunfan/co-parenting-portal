"""
validate-js.py — Validate index.html JS syntax and check common custody logic issues.
Run: python validate-js.py
"""
import re, subprocess, os, sys

def main():
    # Resolve index.html relative to this script (skills/co-parenting-custody/scripts/)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # 3 levels up: scripts -> co-parenting-custody -> skills -> repo root
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
    html_path = os.path.join(repo_root, 'index.html')

    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Extract and syntax-check JS
    m = re.search(r'<script>([\s\S]*?)</script>', html)
    if not m:
        print("ERROR: No <script> block found"); return
    js = m.group(1)
    print(f"[1] JS block: {len(js)} chars")

    tmp = os.path.join(repo_root, '_tmp_validate.js')
    with open(tmp, 'w', encoding='utf-8') as f:
        f.write(js)
    r = subprocess.run(['node', '--check', tmp], capture_output=True, text=True)
    os.remove(tmp)
    if r.returncode == 0:
        print("[1] JS SYNTAX: OK")
    else:
        print(f"[1] JS SYNTAX ERROR: {r.stderr}")
        return

    # 2. Custody logic checks
    issues = []

    # Check: isSummerBreak should appear in each calendar function (SPO and ESPO = 2 is OK)
    summer_count = js.count('const isSummerBreak')
    if summer_count > 2:
        issues.append(f"TOO MANY isSummerBreak declarations ({summer_count}, expected 2: SPO + ESPO)")

    if 'function getSchoolBreakCustody' not in js:
        issues.append("MISSING: getSchoolBreakCustody function")
    if 'function isMomSummerDay' not in js:
        issues.append("MISSING: isMomSummerDay function")

    bounds = re.findall(r'const endYear = (\d+), endMonth = (\d+)', js)
    if bounds:
        uniq = set(bounds)
        if len(uniq) > 1:
            issues.append(f"INCONSISTENT calendar bounds: {uniq}")
        else:
            y, mo = list(uniq)[0]
            print(f"[2] Calendar bounds: endYear={y}, endMonth={mo}")
        if any(int(mo) < 7 for _, mo in bounds):
            issues.append("endMonth < 7: does not cover full summer (set >= 7 for August)")

    # Check Mom summer for 2026 and 2027
    for yr in [2026, 2027]:
        if str(yr) not in js:
            issues.append(f"Missing summer definitions for year {yr}")

    if 'Summer Break' not in html:
        issues.append("Missing 'Summer Break' in schoolBreaks array")

    # Check for stray text lines (plain English outside strings/comments)
    for i, line in enumerate(js.split('\n'), 1):
        s = line.strip()
        if s.startswith('//') or not s or s.startswith('*'):
            continue
        # Heuristic: starts with capital, contains words like "Thu", "after school"
        # but is NOT in a string, NOT a function declaration, NOT a return statement
        if re.match(r"^[A-Z][a-z].*(Thu|after school|summer|week|Mon|Sun)[s]?", s):
            if '"' not in s and "'" not in s and 'function' not in s and 'return' not in s and '=' not in s and 'if' not in s:
                issues.append(f"POSSIBLE STRAY TEXT line {i}: {s[:80]}")

    if issues:
        print("\n[ISSUE SUMMARY]")
        for iss in issues:
            print(f"  - {iss}")
    else:
        print("[2] Custody logic checks: ALL PASSED")

    print("\nDone!")

if __name__ == '__main__':
    main()
