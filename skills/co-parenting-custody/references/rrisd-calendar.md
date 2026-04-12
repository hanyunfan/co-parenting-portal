# RRISD School Calendar Reference

Round Rock ISD, Round Rock, TX — Key Dates

## 2025-2026 School Year
- First day: Aug 25, 2025
- Labor Day: Sep 1, 2025
- Fall Break: Oct 17, 2025
- Thanksgiving: Nov 24–25, 2025
- Winter Break: Dec 22, 2025 – Jan 4, 2026
- MLK Day: Jan 19, 2026
- President's Day: Feb 16, 2026
- Spring Break: Mar 16–20, 2026
- Last day: May 28, 2026
- **Summer Break: May 28 – Aug 16, 2026** (81 days)

## 2026-2027 School Year
- First day: Aug 18, 2026
- Labor Day: Sep 4, 2026
- Fall Break: Nov 23–27, 2026
- Thanksgiving: Nov 23–27, 2026
- Winter Break: Dec 18, 2026 – Jan 3, 2027
- MLK Day: Jan 18, 2027
- President's Day: Feb 15, 2027
- Spring Break: Mar 15–19, 2027
- Last day: May 27, 2027
- **Summer Break: May 27 – Aug 15, 2027** (81 days)

## 2027-2028 (forecast)
- First day: Aug 17, 2027
- Labor Day: Sep 3, 2027
- Fall Break: Oct 15, 2027 (Fri) — single day
- Thanksgiving: Nov 22–26, 2027
- Winter Break: Dec 17, 2027 – Jan 6, 2028
- MLK Day: Jan 16, 2028
- President's Day: Feb 20, 2028
- Spring Break: Mar 12–16, 2028
- Last day: May 26, 2028
- **Summer Break: May 26 – Aug 14, 2028**

---

## School Break Data (in `index.html` `schoolBreaks` array)

```js
const schoolBreaks = [
    // 2025-2026
    { start: '2025-08-25', end: '2025-08-31', label: { en: 'School Year Begins', cn: '开学' } },
    { start: '2025-09-01', end: '2025-09-01', label: { en: 'Labor Day', cn: '劳动节' } },
    { start: '2025-10-17', end: '2025-10-17', label: { en: 'Fall Break', cn: '秋假' } },
    { start: '2025-11-24', end: '2025-11-25', label: { en: 'Thanksgiving', cn: '感恩节' } },
    { start: '2025-12-22', end: '2026-01-04', label: { en: 'Winter Break', cn: '寒假' } },
    { start: '2026-01-19', end: '2026-01-19', label: { en: 'MLK Day', cn: '马丁路德金日' } },
    { start: '2026-02-16', end: '2026-02-16', label: { en: "President's Day", cn: '总统日' } },
    { start: '2026-03-16', end: '2026-03-20', label: { en: 'Spring Break', cn: '春假' } },
    { start: '2026-05-28', end: '2026-08-16', label: { en: 'Summer Break', cn: '暑假' } },
    // 2026-2027
    { start: '2026-08-17', end: '2026-08-17', label: { en: 'School Year Begins', cn: '开学' } },
    { start: '2026-09-04', end: '2026-09-04', label: { en: 'Labor Day', cn: '劳动节' } },
    { start: '2026-11-23', end: '2026-11-27', label: { en: 'Fall Break', cn: '秋假' } },
    { start: '2026-12-18', end: '2027-01-03', label: { en: 'Winter Break', cn: '寒假' } },
    { start: '2027-01-18', end: '2027-01-18', label: { en: 'MLK Day', cn: '马丁路德金日' } },
    { start: '2027-02-15', end: '2027-02-15', label: { en: "President's Day", cn: '总统日' } },
    { start: '2027-03-15', end: '2027-03-19', label: { en: 'Spring Break', cn: '春假' } },
    { start: '2027-05-27', end: '2027-08-15', label: { en: 'Summer Break', cn: '暑假' } },
];
```
