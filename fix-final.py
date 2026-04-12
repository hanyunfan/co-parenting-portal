with open('C:/Users/frank/.openclaw/workspace/projects/co-parenting-portal/index.html', 'r', encoding='utf-8', newline='\n') as f:
    c = f.read()

# 1. Extend calendar to August 2027 (endMonth=7)
old_bounds = "const startYear = 2026, startMonth = 3;\n    const endYear = 2027, endMonth = 4;"
new_bounds = "const startYear = 2026, startMonth = 3;\n    const endYear = 2027, endMonth = 7;  // Through August 2027 (end of RRISD summer break)"
if old_bounds in c:
    c = c.replace(old_bounds, new_bounds)
    print("1. Calendar extended to August 2027 OK")
else:
    print("1. Calendar bounds NOT FOUND")

# 2. Add getSchoolBreakCustody function BEFORE generateESPOCalendar
# This handles spring/winter break split (Mom first half, Dad second half)
# Summer break is handled separately (Dad 30 days, Mom remaining)
old_func = "// ESPO Calendar: Extended Possession"
new_func = """// Returns 'dad' or 'mom' for school break days, or 'none' if not a break.
// Spring/Winter breaks: split evenly, Mom gets first half, Dad second half.
// Summer: handled separately via isDadSummerDay / isMomSummerDay.
function getSchoolBreakCustody(dateStr) {
    const d = new Date(dateStr);
    // RRISD Spring Break 2027: March 15-19
    if (d >= new Date(2027, 2, 15) && d <= new Date(2027, 2, 19)) {
        // 5 days: Mom gets 3 (Mon-Wed), Dad gets 2 (Thu-Fri)
        const dayOfBreak = Math.floor((d - new Date(2027, 2, 15)) / (1000*60*60*24));
        return dayOfBreak < 3 ? 'mom' : 'dad';
    }
    // RRISD Winter Break 2026-2027: Dec 18 - Jan 3 (17 days)
    // Split: Mom gets Dec 18-25 (8 days), Dad gets Dec 26 - Jan 3 (9 days)
    const winStart = new Date(2026, 11, 18); // Dec 18
    const winEnd = new Date(2027, 0, 3);      // Jan 3
    if (d >= winStart && d <= winEnd) {
        const dayOfBreak = Math.floor((d - winStart) / (1000*60*60*24));
        return dayOfBreak < 8 ? 'mom' : 'dad';
    }
    return 'none';
}

function isMomSummerDay(day, month, year) {
    // Mom's remaining summer days: July 31 + Aug 1-2 (after Dad's 30 days)
    if (month === 6 && day === 31) return true; // July 31
    if (month === 7 && day >= 1 && day <= 2) return true; // Aug 1-2
    return false;
}

"""
if new_func in c:
    print("2. School break functions already present")
else:
    c = c.replace("// ESPO Calendar: Extended Possession", new_func)
    print("2. School break functions added OK")

# 3. Update the SPO calendar end year too
old_spo_bounds = "// SPO Calendar: Standard Possession"
spo_end = c.find("function generateSPOCalendar")
spo_end += c[spo_end:].find("const endYear")
old_spo = "const endYear = 2027, endMonth = 4;"
new_spo = "const endYear = 2027, endMonth = 7;"
if old_spo in c:
    c = c.replace(old_spo, new_spo)
    print("3. SPO calendar extended OK")
else:
    print("3. SPO bounds NOT FOUND")

# 4. Add summer-mom CSS class
old_css = ".cal-day.summer-mom { background: rgba(255,107,107,0.15); }"
if old_css in c:
    print("4. summer-mom CSS already present")
else:
    old_css2 = ".cal-day.summer-dad { background: rgba(155,89,232,0.5); border: 2px solid rgba(155,89,232,0.8); }"
    new_css2 = ".cal-day.summer-dad { background: rgba(155,89,232,0.5); border: 2px solid rgba(155,89,232,0.8); }\n        .cal-day.summer-mom { background: rgba(255,107,107,0.2); }"
    if old_css2 in c:
        c = c.replace(old_css2, new_css2)
        print("4. summer-mom CSS added OK")
    else:
        print("4. Could not find CSS to add summer-mom")

# 5. Update extendedDad i18n text (EN and CN)
old_dad_en = "extendedDad: 'Father: 1st, 3rd, 5th week Thu after school - Sun 6PM (+ Mon AM if school off) + 30 consecutive days in summer; weeks 2 & 4: every Thu 6PM-8PM (standard SPO)',"
new_dad_en = "extendedDad: 'Father: 1st/3rd/5th week Thu after school-Sun 6PM (+ Mon AM if school off) + 30 consecutive days in summer (Jul 1-30, default); weeks 2 & 4: every Thu after school (standard SPO). Mother: spring/winter break first half; summer remaining days (Jul 31 + Aug 1-2).',"
if old_dad_en in c:
    c = c.replace(old_dad_en, new_dad_en)
    print("5. extendedDad EN updated OK")
else:
    print("5. extendedDad EN NOT FOUND")

old_dad_cn = "extendedDad: '父亲：每月第1、3、5周周四放学后至周日6点（+周一早上如果学校不上课）+ 夏季30天；第2、4周：每周四下午6点至8点（标准SPO）',"
new_dad_cn = "extendedDad: '父亲：每月第1/3/5周周四放学后至周日6点（+周一早上如果学校不上课）+ 夏季30天（默认7月1-30日）；第2/4周：每周四放学后（标准SPO）。母亲：春假/寒假前半段；暑假剩余天数（7月31日+8月1-2日）。',"
if old_dad_cn in c:
    c = c.replace(old_dad_cn, new_dad_cn)
    print("5b. extendedDad CN updated OK")
else:
    print("5b. extendedDad CN NOT FOUND")

# 6. Also update HTML static text for extendedDad
old_dad_html = '<p id="extendedDad">Father: 1st, 3rd, 5th week Thu after school - Sun 6 PM + 30 days summer; plus every Thu 6-8 PM on weeks 2 & 4</p>'
new_dad_html = '<p id="extendedDad">Father: 1st/3rd/5th week Thu after school-Sun 6PM (+ Mon AM if school off) + 30 consecutive days in summer (Jul 1-30, default); weeks 2 & 4: every Thu after school (standard SPO). Mother: spring/winter break first half; summer remaining days (Jul 31 + Aug 1-2).</p>'
if old_dad_html in c:
    c = c.replace(old_dad_html, new_dad_html)
    print("6. extendedDad HTML updated OK")
else:
    print("6. extendedDad HTML NOT FOUND")

# 7. Update the ESPO day loop to use school break custody
# Find and replace the isDadSummerDay block and the holiday/school break block
old_espo_block = """            const isDadSummerDay = isSummerBreak && (month === 6 && d >= 1 && d <= 30);
            // This day's weekend is ESPO if:
            //   - It is Thu/Fri/Sat/Sun AND its Thursday is in espothuSet (1st/3rd/5th Thu of month)
            //   - OR its Thursday belongs to Weekend 1 of NEXT month (e.g. Apr 30)
            const dowIsESPO = (isThursday || isFriday || isSaturday || isSunday);
            // Find Thursday of this week
            const mondayOfWeek = new Date(year, month, d);
            mondayOfWeek.setDate(d - (dow === 0 ? 6 : dow - 1));
            const thursdayOfWeek = new Date(mondayOfWeek);
            thursdayOfWeek.setDate(mondayOfWeek.getDate() + 3);
            const thuOfWeek = thursdayOfWeek.getDate();
            const thursdayOfWeekMonth = thursdayOfWeek.getMonth();
            const thursdayOfWeekYear = thursdayOfWeek.getFullYear();
            // Is this day's Thursday in espothuSet AND in the same month?
            const isThuInESPOSet = thursdayOfWeekMonth === month && thursdayOfWeekYear === year && espothuSet.has(thuOfWeek);
            // Is this day's Thursday one whose weekend belongs to next month? (Apr 30 case)
            const isThuNextMonthWeekend = thursdayOfWeekMonth !== month || thursdayOfWeekYear !== year;
            const isThisDayESPO = dowIsESPO && (isThuInESPOSet || isThuNextMonthWeekend);
            const isThuNonESPO = isThursday && !isThisDayESPO && !isSummerBreak;
            if (isDadSummerDay) {
                dayDiv.classList.add('summer-dad');
                labelDiv.textContent = lang === 'cn' ? '爸爸(暑假30天)' : 'Dad-Sum';
            } else if (isHoliday && !isThisDayESPO) {
                dayDiv.classList.add('holiday');
                labelDiv.textContent = (breakInfo.label[lang] || breakInfo.label.en);
            } else if (natHoliday) {
                dayDiv.classList.add('national-holiday');
                labelDiv.textContent = natHoliday[lang] || natHoliday.en;
            } else if (isThisDayESPO) {
                dayDiv.classList.add('dad');
                if (isThursday) labelDiv.textContent = lang === 'cn' ? '爸爸ESPO' : 'Dad-ESPO';
                else if (isSunday) labelDiv.textContent = lang === 'cn' ? '爸爸(周一早)' : 'Dad-Sun';
                else labelDiv.textContent = lang === 'cn' ? '爸爸' : 'Dad';
            } else if (isThuNonESPO) {
                dayDiv.classList.add('dad-partial');
                labelDiv.textContent = lang === 'cn' ? '放学后至次日上學' : 'Dad (after school)';
            } else if (isThursday && isSummerBreak) {
                dayDiv.classList.add('mom');
            } else {
                dayDiv.classList.add('mom');
            }"""

new_espo_block = """            const isDadSummerDay = isSummerBreak && (month === 6 && d >= 1 && d <= 30);
            const isMomSummerDay_val = isSummerBreak && isMomSummerDay(d, month, year);
            // School break custody: Mom first half, Dad second half
            const breakCustody = isHoliday ? getSchoolBreakCustody(dateStr) : 'none';
            // This day's weekend is ESPO if:
            //   - It is Thu/Fri/Sat/Sun AND its Thursday is in espothuSet (1st/3rd/5th Thu of month)
            //   - OR its Thursday belongs to Weekend 1 of NEXT month (e.g. Apr 30)
            const dowIsESPO = (isThursday || isFriday || isSaturday || isSunday);
            // Find Thursday of this week
            const mondayOfWeek = new Date(year, month, d);
            mondayOfWeek.setDate(d - (dow === 0 ? 6 : dow - 1));
            const thursdayOfWeek = new Date(mondayOfWeek);
            thursdayOfWeek.setDate(mondayOfWeek.getDate() + 3);
            const thuOfWeek = thursdayOfWeek.getDate();
            const thursdayOfWeekMonth = thursdayOfWeek.getMonth();
            const thursdayOfWeekYear = thursdayOfWeek.getFullYear();
            // Is this day's Thursday in espothuSet AND in the same month?
            const isThuInESPOSet = thursdayOfWeekMonth === month && thursdayOfWeekYear === year && espothuSet.has(thuOfWeek);
            // Is this day's Thursday one whose weekend belongs to next month? (Apr 30 case)
            const isThuNextMonthWeekend = thursdayOfWeekMonth !== month || thursdayOfWeekYear !== year;
            // School break overrides ESPO weekend; if no break, use ESPO
            const isThisDayESPO = (isHoliday && breakCustody !== 'none') ? false : (dowIsESPO && (isThuInESPOSet || isThuNextMonthWeekend));
            const isThuNonESPO = isThursday && !isThisDayESPO && !isSummerBreak && !isHoliday;
            // Priority: 1) Dad summer 30 days, 2) Mom summer remaining, 3) school break, 4) ESPO/partial
            if (isDadSummerDay) {
                dayDiv.classList.add('summer-dad');
                labelDiv.textContent = lang === 'cn' ? '爸爸(暑假30天)' : 'Dad-Sum';
            } else if (isMomSummerDay_val) {
                dayDiv.classList.add('summer-mom');
                labelDiv.textContent = lang === 'cn' ? '妈妈(暑假剩余)' : 'Mom-Sum';
            } else if (isHoliday) {
                // School break: show label, color by custody
                dayDiv.classList.add(breakCustody === 'mom' ? 'mom' : 'dad');
                labelDiv.textContent = (breakInfo.label[lang] || breakInfo.label.en);
            } else if (natHoliday) {
                dayDiv.classList.add('national-holiday');
                labelDiv.textContent = natHoliday[lang] || natHoliday.en;
            } else if (isThisDayESPO) {
                dayDiv.classList.add('dad');
                if (isThursday) labelDiv.textContent = lang === 'cn' ? '爸爸ESPO' : 'Dad-ESPO';
                else if (isSunday) labelDiv.textContent = lang === 'cn' ? '爸爸(周一早)' : 'Dad-Sun';
                else labelDiv.textContent = lang === 'cn' ? '爸爸' : 'Dad';
            } else if (isThuNonESPO) {
                dayDiv.classList.add('dad-partial');
                labelDiv.textContent = lang === 'cn' ? '放学后至次日上學' : 'Dad (after school)';
            } else {
                dayDiv.classList.add('mom');
            }"""

if old_espo_block in c:
    c = c.replace(old_espo_block, new_espo_block)
    print("7. ESPO day loop updated OK")
else:
    print("7. ESPO day loop NOT FOUND")
    idx = c.find("const isDadSummerDay = isSummerBreak")
    print(f"isDadSummerDay at {idx}")
    print(repr(c[idx:idx+300]))

# 8. Verify no duplicate const isSummerBreak
count_summer = c.count("const isSummerBreak = breakInfo")
print(f"8. const isSummerBreak count: {count_summer} (should be 1)")

# 9. Verify getSchoolBreakCustody is present
if "function getSchoolBreakCustody" in c:
    print("9. getSchoolBreakCustody function present OK")
else:
    print("9. getSchoolBreakCustody NOT FOUND")

with open('C:/Users/frank/.openclaw/workspace/projects/co-parenting-portal/index.html', 'w', encoding='utf-8', newline='\n') as f:
    f.write(c)
print("Done!")
