# Co-Parenting Calendar Logic - Priority Layers

## Priority Stack (highest → lowest)
1. **Father's Day** (Fri-Sat-Sun weekend, pink fd-mdspecial)
2. **Mother's Day** (Fri-Sat-Sun weekend, pink fd-mdspecial)
3. **School Breaks** (Spring/Winter/Summer)
4. **National Holidays** (Thanksgiving, Christmas, etc.)
5. **ESPO Base** (Dad 1st/3rd/5th Thu evening→Sun, Mom rest)

## Layer 1: School Breaks Calendar

### Summer
- RRISD 2025-2026: May 28 – Aug 16
- RRISD 2026-2027: May 27 – Aug 15
- **Dad gets July 1-30 (30 consecutive days)** ← §153.317 default
- **Mom gets** summer start → June 30 + July 31 → summer end
  - 2026: May 28-31 (4 days) + July 31-Aug 16 (17 days) = 21 mom days
  - 2027: May 27-31 (5 days) + July 31-Aug 15 (16 days) = 21 mom days

### Spring Break
- RRISD 2026: March 16-20
- RRISD 2027: March 15-19
- §153.312(b)(1): **Even year = Dad whole; Odd year = Mom whole**

### Winter Break (includes Christmas)
- RRISD 2026-2027: Dec 18 – Jan 3
- **Split at Dec 28 (inclusive for first parent)**
  - Even year (2026): Dad gets Dec 18-28, Mom gets Dec 29-Jan 3
  - Odd year (2027): Mom gets Dec 18-28, Dad gets Dec 29-Jan 3

## Layer 2: ESPO Base Calendar
- Dad: 1st/3rd/5th week = Thu after school → Sun 6PM (+ Mon morning if school off)
- Weekends labeled by the Thursday that STARTS them (1st/3rd/5th Thu of month)
- 2nd/4th week: Dad gets Thu after school only (standard SPO)

## Implementation Plan
Build layered calendar by computing each layer, then applying priority:
```
For each day:
  if (isFD) → fd-mdspecial pink
  else if (isMD) → fd-mdspecial pink
  else if (isSchoolBreak) → use school break custody (mom/dad/summer-mom/summer-dad)
  else if (isNationalHoliday) → national-holiday orange (but show Dad/Mom label for Thanksgiving/Christmas)
  else → use ESPO base (dad or mom)
```
