---
name: co-parenting-custody
description: Maintain and update the co-parenting-portal (https://hanyunfan.github.io/co-parenting-portal), a Texas child custody schedule calculator for RRISD parents. Use when asked to update the calendar, fix custody rules, add school breaks, modify summer/winter/spring break handling, or apply any Texas Family Code logic to the portal. Also use when debugging calendar display issues, button failures, or ESPO weekend assignments.
---

# Co-Parenting Custody Portal — Maintenance Skill

Single-file app: `index.html` — all EN/CN i18n, calendar rendering, custody logic.

---

## Project Overview

- **GitHub**: https://github.com/hanyunfan/co-parenting-portal
- **Live**: https://hanyunfan.github.io/co-parenting-portal
- **Calendar range**: April 2026 – August 2027 (update `endMonth` as needed)
- **School district**: Round Rock ISD (RRISD), Round Rock, TX

## Custody Rules Summary

### Standard Possession Order (SPO) — Texas §153.310
Father: Every Thursday 6:00 PM – 8:00 PM. All other times: Mother.

### Extended Possession Order (ESPO) — Texas §153.317
Father: 1st, 3rd, 5th Thursday after school → Sunday 6 PM (+ Monday morning school dropoff). Weeks 2 & 4: standard Thursday 6–8 PM.

**Weekend number** = count of Fridays in the month that are STRICTLY LESS than the week's Friday. The week's Friday = Friday on or after (Monday + 4). This correctly handles month-boundary Thursdays (Apr 30 → Weekend 1 of May).

### Summer Break — Texas §153.314 / §153.317
- SPO/ESPO suspended during summer break (no school = no after-school pickup)
- Dad gets **30 consecutive days** (default: July 1–30)
- Mom gets remaining summer days (after Dad's 30 end)
  - 2026: Mom gets July 31, Aug 1, Aug 2 (school starts Aug 3)
  - 2027: Mom gets July 31, Aug 1–15 (school starts Aug 16)
- July 4 (Independence Day): national-holiday label overrides summer custody

### School Break Split — Texas standard
During spring/winter break (when school is out), parents split the break:
- **Odd years** (2027, 2029, …): Mom gets first half, Dad gets second half
- **Even years** (2026, 2028, …): Dad gets first half, Mom gets second half
- Half = `floor(totalDays / 2)`, remainder goes to second parent

**Priority order** (highest first):
1. School break split (overrides everything)
2. Dad summer 30 days
3. Mom summer remaining days
4. National holidays
5. ESPO weekend / partial Thursday

---

## Key Functions (in `index.html`)

| Function | Location (approx) | Purpose |
|---|---|---|
| `getThursdayWeekLabel` | ~line 676 | Returns which weekend number (1-5) a Thursday belongs to |
| `isESPOWeek` | ~line 701 | Returns `{label, nextMonth}` for a given Thursday |
| `isESPOWeekend` | ~line 707 | True if given day is in an ESPO weekend |
| `getSchoolBreakCustody` | before `generateESPOCalendar` | Returns `'dad'`, `'mom'`, or `'none'` for school break days |
| `isMomSummerDay` | before `generateESPOCalendar` | True for Mom's designated summer days after Dad's 30 |
| `generateESPOCalendar` | ~line 800 | Renders ESPO calendar |
| `generateSPOCalendar` | ~line 720 | Renders SPO calendar |
| `getNationalHolidayLabel` | ~line 576 | Returns national holiday label for a date |
| `isSchoolBreak` | ~line 635 | Returns school break object or null |

---

## Common Fix Tasks

### Adding a new school break
Edit `schoolBreaks` array (~line 613). Add entry:
```js
{ start: 'YYYY-MM-DD', end: 'YYYY-MM-DD', label: { en: 'Break Name', cn: '中文名' } }
```
Then update `getSchoolBreakCustody` if the break needs split custody handling.

### Extending calendar range
Update both `generateSPOCalendar` and `generateESPOCalendar`:
```js
const endYear = YYYY, endMonth = M;  // month 0-indexed (7 = August)
```

### Modifying Mom's summer days
Edit `isMomSummerDay(day, month, year)`. Add a year-specific block:
```js
if (year === YYYY && month === M && day >= D1 && day <= D2) return true;
```

### Verifying no JS syntax errors
Run Node.js on the script block:
```js
const fs = require('fs');
const m = fs.readFileSync('index.html','utf8').match(/<script>([\s\S]*?)<\/script>/);
try { new Function(m[1]); console.log('JS OK'); }
catch(e) { console.log('JS ERROR:', e.message); }
```

### Debugging button failures
1. Check browser console for JS errors
2. Run the Node.js validation above
3. Check for duplicate `const` declarations (e.g., double `const isSummerBreak`)
4. Check for stray text/strings outside of proper JS syntax

---

## RRISD School Calendar Reference

See `references/rrisd-calendar.md` for full key dates.
