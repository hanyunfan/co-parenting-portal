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

---

## Texas Family Code References

- **§153.314** — Holiday Possession (supersedes all other schedules)
- **§153.317** — Extended Standard Possession Order (ESPO)
- **§154.001** — Child Support Guidelines (expenses page)

---

## Custody Priority Order (highest → lowest)

This is the single most important rule: **higher priority always overrides lower priority.**

| # | Type | Rule | § |
|---|------|------|---|
| 1 | **Father's / Mother's Day** | Fri 6pm → Sun 6pm of that weekend | §153.314(5)(6) |
| 2 | **Christmas** | Even yr: Dad Dec18noon–Dec28noon, then Mom; Odd yr: swap | §153.314(1)(2) |
| 3 | **Thanksgiving** | Odd yr: Dad Wed6pm–Sun6pm; Even yr: Mom Wed6pm–Sun6pm | §153.314(3) |
| 4 | **New Year's Day** | Odd yr: Dad; Even yr: Mom (Jan 1 noon–midnight) | §153.314 |
| 5 | **Other national holidays** | Alternating by year (MLK, Presidents', Memorial, Labor, etc.) | §153.314 |
| 6 | **Summer Break** | Dad Jun 1–30 (30 consecutive days); Mom Jul31 + Aug1–15 | §153.317 |
| 7 | **Spring / Winter Break** | Odd yr: Dad 2nd half; Even yr: Dad 1st half | §153.317 |
| 8 | **ESPO 1st/3rd/5th Week** | Thu after school → Mon morning school = Dad | §153.317 |
| 9 | **ESPO 2nd/4th Thursday** | Dad 6pm–8pm only (then Mom) | §153.311 |

### Key §153.314 Dates
- **Father's Day**: 3rd Sunday of June, Dad gets Fri 6pm → Sun 6pm
- **Mother's Day**: 2nd Sunday of May, Mom gets Fri 6pm → Sun 6pm
- **Christmas swap**: Dec 28 noon — whoever had Dec 18–Dec 27 gives up at noon Dec 28
- **Thanksgiving**: begins 6pm when school dismisses (usually the Wednesday before)
- **New Year's Day**: Jan 1 (odd=Dad, even=Mom)

### Christmas Rotation (Winter Break)
The Christmas school vacation runs Dec 18 – Jan 3 (RRISD). The statutory split:
- **Even year (2026)**: Dad gets Dec 18 noon → Dec 28 noon; Mom Dec 28 noon → Jan 3 6pm
- **Odd year (2027)**: Mom gets Dec 18 noon → Dec 28 noon; Dad Dec 28 noon → Jan 3 6pm
- Jan 1 is also New Year's Day — if the parent who has Christmas has New Year's, it is included. If not, New Year's is a separate day.

### Thanksgiving Rotation
School dismisses Wed afternoon. Possession: Wed 6pm → following Sun 6pm.
- **Odd year**: Dad gets Wed–Sun
- **Even year**: Mom gets Wed–Sun

---

## School Break Custody Split

During school breaks (when classes are not in session), parents split the break evenly:
- **Odd years**: Dad gets 2nd half; Mom gets 1st half
- **Even years**: Dad gets 1st half; Mom gets 2nd half

Half calculation: `halfLen = Math.floor(totalDays / 2)`
- First `halfLen` days → first parent; remaining days → second parent

---

## Summer Break

SPO/ESPO regular schedule is SUSPENDED during summer break (no school = no after-school pickup).
- **Dad**: 30 consecutive days (default: July 1–30)
- **Mom**: all remaining summer days
  - 2026: Mom gets July 31, Aug 1, Aug 2 (school starts Aug 3)
  - 2027: Mom gets July 31, Aug 1–15 (school starts Aug 16)

---

## ESPO Weekend Logic

Weekend = Thursday (after school) → Sunday 6pm.

**Which weeks are 1st/3rd/5th (Dad's)?**

Weekend is identified by the **Friday that starts it**. Weekend number = count of Fridays in the month strictly before that Friday.

```js
// Weekend 1 of next month: when the week's Friday falls in the following month
// (e.g., Apr 30's Thursday → Weekend 1 of May)
function isESPOWeekendDay(year, month, day) {
    // Find the Friday of this week
    const dow = new Date(year, month, day).getDay();
    const mondayOfWeek = new Date(year, month, day);
    mondayOfWeek.setDate(day - (dow === 0 ? 6 : dow - 1));
    const friOfWeek = new Date(mondayOfWeek);
    friOfWeek.setDate(mondayOfWeek.getDate() + 4);
    const friDay = friOfWeek.getDate(), friMonth = friOfWeek.getMonth();
    // If Friday is in different month → Weekend 1 of next month = ESPO
    if (friMonth !== month) return true;
    // Count Fridays in this month before friDay
    let friCount = 0;
    for (let fd = 1; fd < friDay; fd++) {
        if (new Date(year, month, fd).getDay() === 5) friCount++;
    }
    return [1, 3, 5].includes(friCount + 1);
}
```

---

## Key Functions (in `index.html`)

| Function | Purpose |
|---|---|
| `getFathersDayWeekend(dateStr)` | Returns true if date is in Father's Day weekend (Fri–Sun) |
| `getMothersDayWeekend(dateStr)` | Returns true if date is in Mother's Day weekend (Fri–Sun) |
| `getChristmasCustody(dateStr)` | Returns 'dad'/'mom'/'none' for Christmas period |
| `getThanksgivingCustody(dateStr)` | Returns 'dad'/'mom'/'none' for Thanksgiving period |
| `getNewYearCustody(dateStr)` | Returns 'dad'/'mom'/'none' for New Year's Day |
| `getSchoolBreakCustody(dateStr)` | Returns 'dad'/'mom'/'none' for spring/winter break days |
| `isMomSummerDay(year, month, day)` | Returns true for Mom's remaining summer days |
| `isESPOWeekendDay(year, month, day)` | True if the Friday of this week is 1st/3rd/5th Friday |
| `isInDadESPOMonth(year, month, day)` | True if this day is Thu/Fri/Sat/Sun of an ESPO weekend |
| `isDadThursdayNonESPO(year, month, day)` | True if this is a Week 2/4 Thursday (Dad 6–8pm only) |
| `isSchoolBreak(dateStr)` | Returns break object or null |
| `getHolidayName(year, month, day)` | Returns statutory holiday object or null |

---

## Adding / Modifying School Breaks

Edit `schoolBreaks` array in `index.html`. Add entry:
```js
{ start: 'YYYY-MM-DD', end: 'YYYY-MM-DD', label: { en: 'Break Name', cn: '中文名' } }
```

Spring Break and Winter Break custody is handled by `getSchoolBreakCustody()` — no separate update needed unless the split rule changes.

---

## Extending Calendar Range

Update in both `generateSPOCalendar()` and `generateESPOCalendar()`:
```js
const endYear = YYYY, endMonth = M;  // 0-indexed (7 = August)
```

---

## RRISD School Calendar Reference

See `references/rrisd-calendar.md` for full key dates.

---

## Verifying No JS Errors

```js
const fs = require('fs');
const m = fs.readFileSync('index.html','utf8').match(/<script>([\s\S]*?)<\/script>/);
try { new Function(m[1]); console.log('JS OK'); }
catch(e) { console.log('JS ERROR:', e.message); }
```

## Debugging Button Failures
1. Check browser console for JS errors
2. Run the Node.js validation above
3. Check for duplicate `const` declarations
4. Check for stray text/strings outside of proper JS syntax
