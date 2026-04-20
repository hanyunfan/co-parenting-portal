"""
custody_interval_calculator -- interval_generator.py
====================================================
Core module: generates continuous, non-overlapping custody intervals
using an ordered array + binary search for O(log n) queries.

Rules are read from the calendar JSON (custody_rules section) so they can
be modified without changing code. Supports SPO and ESPO modes.
"""
import json
import bisect
import calendar as calmod
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Literal

# ─── Data Structures ────────────────────────────────────────────────────────

@dataclass
class CustodyInterval:
    """A [start, end] inclusive date range with a single custodian."""
    start: date
    end: date
    custodian: Literal["dad", "mom"]
    reason: str

    def __repr__(self):
        return f"CustodyInterval({self.start}->{self.end}, {self.custodian}, {self.reason})"


class IntervalList:
    """Ordered list of CustodyIntervals, O(log n) query via bisect."""

    def __init__(self):
        self._intervals: list[CustodyInterval] = []

    def append(self, interval: CustodyInterval) -> None:
        bisect.insort(self._intervals, interval, key=lambda i: i.start)

    def extend(self, intervals) -> None:
        for iv in intervals:
            bisect.insort(self._intervals, iv, key=lambda i: i.start)

    def query(self, d: date) -> CustodyInterval | None:
        if not self._intervals:
            return None
        starts = [i.start for i in self._intervals]
        idx = bisect.bisect_right(starts, d) - 1
        if idx < 0:
            return None
        interval = self._intervals[idx]
        if interval.start <= d <= interval.end:
            return interval
        return None

    def query_range(self, start: date, end: date) -> list[CustodyInterval]:
        if not self._intervals:
            return []
        starts = [i.start for i in self._intervals]
        left = max(0, bisect.bisect_right(starts, start) - 1)
        result = []
        for interval in self._intervals[left:]:
            if interval.start > end:
                break
            if interval.end >= start:
                result.append(interval)
        return result

    def verify_no_overlaps(self) -> list[str]:
        errors = []
        for i in range(len(self._intervals) - 1):
            a = self._intervals[i]
            b = self._intervals[i + 1]
            if a.end >= b.start:
                errors.append(f"OVERLAP: {a} overlaps with {b}")
        return errors

    def __len__(self):
        return len(self._intervals)

    def __iter__(self):
        return iter(self._intervals)

    def __getitem__(self, idx):
        return self._intervals[idx]

    def dump(self) -> list[dict]:
        return [
            {"start": str(i.start), "end": str(i.end),
             "custodian": i.custodian, "reason": i.reason}
            for i in self._intervals
        ]


# ─── Calendar Data Types ─────────────────────────────────────────────────────

@dataclass
class SchoolBreak:
    start: str
    end: str
    label: dict

@dataclass
class NoSchoolDay:
    date: str
    label: dict

@dataclass
class SchoolYear:
    year: str
    start: str
    end: str
    breaks: dict[str, SchoolBreak] = field(default_factory=dict)
    noschool_days: list[NoSchoolDay] = field(default_factory=list)

@dataclass
class StandardCalendar:
    district: str
    school_years: list[SchoolYear] = field(default_factory=list)
    source: str = ""
    collected_at: str = ""
    default_mode: str = "espo"
    custody_rules: dict = field(default_factory=dict)


# ─── Interval Generator ─────────────────────────────────────────────────────

class CustodyIntervalGenerator:
    """
    Generates custody intervals from a StandardCalendar.
    Reads rules from calendar.custody_rules[mode] (JSON config).
    """

    def __init__(self, calendar: StandardCalendar, mode: str = None):
        self.calendar = calendar
        self.mode = mode or calendar.default_mode or "espo"
        self.rules = self.calendar.custody_rules.get(self.mode, {})
        self._no_school_dates: set[date] = set()
        self._build_noschool_set()

    def _build_noschool_set(self) -> None:
        for sy in self.calendar.school_years:
            for nd in sy.noschool_days:
                self._no_school_dates.add(date.fromisoformat(nd.date))

    def _sy_year(self, d: date) -> int:
        for sy in self.calendar.school_years:
            sy_start = date.fromisoformat(sy.start)
            sy_end = date.fromisoformat(sy.end)
            if sy_start <= d <= sy_end:
                return int(sy.year.split("-")[0])
        return d.year

    def _is_odd_year(self, d: date) -> bool:
        return self._sy_year(d) % 2 == 1

    # ── Holiday intervals from JSON rules ────────────────────────────────────

    def _thanksgiving_intervals(self, sy: SchoolYear):
        br = sy.breaks.get("thanksgiving")
        if not br:
            return []
        start_d = date.fromisoformat(br.start)
        end_d = date.fromisoformat(br.end)
        h_rules = self.rules.get("holidays", {}).get("thanksgiving", {})
        split = h_rules.get("split", "whole")
        if split == "whole":
            parent = h_rules.get("odd_year_parent" if self._is_odd_year(start_d) else "even_year_parent", "dad")
            return [CustodyInterval(start_d, end_d, parent, "thanksgiving")]
        return []

    def _christmas_intervals(self, sy: SchoolYear):
        """
        Christmas per §153.314: even year = Dad first half, odd year = Mom first half.
        Split at Dec 28 noon. We treat Dec 19-28 as first half, Dec 29 - Jan 5 as second.
        """
        br = sy.breaks.get("christmas")
        if not br:
            return []
        start_d = date.fromisoformat(br.start)
        end_d = date.fromisoformat(br.end)
        split_date = date(start_d.year, 12, 28)
        if split_date < start_d:
            split_date = start_d + timedelta(days=(end_d - start_d).days // 2)
        calendar_year = start_d.year
        is_even = calendar_year % 2 == 0
        first_parent = "dad" if is_even else "mom"
        second_parent = "mom" if is_even else "dad"
        return [
            CustodyInterval(start_d, split_date, first_parent, "christmas_first_half"),
            CustodyInterval(split_date + timedelta(days=1), end_d, second_parent, "christmas_second_half"),
        ]

    def _spring_break_intervals(self, sy: SchoolYear):
        br = sy.breaks.get("spring")
        if not br:
            return []
        start_d = date.fromisoformat(br.start)
        end_d = date.fromisoformat(br.end)
        h_rules = self.rules.get("holidays", {}).get("spring_break", {})
        parent = h_rules.get("odd_year_parent" if self._is_odd_year(start_d) else "even_year_parent", "dad")
        return [CustodyInterval(start_d, end_d, parent, "spring_break")]

    def _summer_intervals(self, sy: SchoolYear, holiday_dates: set = None):
        """
        Summer: Dad gets 30 consecutive days (default July 1-30).
        Configurable via custody_rules.
        """
        br = sy.breaks.get("summer")
        if not br:
            return []
        summer_start = date.fromisoformat(br.start)
        summer_end = date.fromisoformat(br.end)
        summer_rule = self.rules.get("summer", {})
        dad_parent = summer_rule.get("parent", "dad")
        default_range = summer_rule.get("default_30_days", "july_1_30")
        if default_range == "july_1_30":
            dad_start = date(summer_start.year, 7, 1)
            dad_end = date(summer_start.year, 7, 30)
        else:
            # Configured custom range — parse from custody rules
            custom = summer_rule.get("custom_range", {})
            dad_start = date(summer_start.year, int(custom.get("start_month", 7)), int(custom.get("start_day", 1)))
            dad_end = date(summer_start.year, int(custom.get("end_month", 7)), int(custom.get("end_day", 30)))
        holiday_dates = holiday_dates or set()
        intervals = []
        if summer_start <= dad_start:
            pre = []
            d = summer_start
            while d < dad_start:
                if d not in holiday_dates:
                    pre.append(d)
                d += timedelta(days=1)
            if pre:
                g_start = g_end = pre[0]
                for rd in pre[1:]:
                    if rd == g_end + timedelta(days=1):
                        g_end = rd
                    else:
                        intervals.append(CustodyInterval(g_start, g_end, "mom", "summer_mom_before_dad"))
                        g_start = g_end = rd
                intervals.append(CustodyInterval(g_start, g_end, "mom", "summer_mom_before_dad"))
        intervals.append(CustodyInterval(dad_start, dad_end, dad_parent, "summer_dad_30_days"))
        # Extend mom_after_dad to cover Aug 12 - (school_start - 1), since no school on those days
        # and they fall between summer break end and the next school year start
        # Extend mom_after_dad to cover Aug 12 - (school_start_next - 1)
        # Days between summer break end and next school year start belong to Mom
        school_start_next = None
        for sy_check in self.calendar.school_years:
            sy_year_num = int(sy_check.year.split("-")[1])
            current_sy_year_num = int(sy.year.split("-")[1])
            if sy_year_num == current_sy_year_num + 1:
                school_start_next = date.fromisoformat(sy_check.start)
                break
        remainder_start = dad_end + timedelta(days=1)
        remainder_end = summer_end
        if school_start_next and school_start_next > summer_end + timedelta(days=1):
            remainder_end = school_start_next - timedelta(days=1)
        else:
            remainder_end = summer_end
        if remainder_start <= remainder_end:
            remainder = []
            d = remainder_start
            while d <= remainder_end:
                if d not in holiday_dates:
                    remainder.append(d)
                d += timedelta(days=1)
            if remainder:
                g_start = g_end = remainder[0]
                for rd in remainder[1:]:
                    if rd == g_end + timedelta(days=1):
                        g_end = rd
                    else:
                        intervals.append(CustodyInterval(g_start, g_end, "mom", "summer_mom_after_dad"))
                        g_start = g_end = rd
                intervals.append(CustodyInterval(g_start, g_end, "mom", "summer_mom_after_dad"))
        return intervals

    def _fathers_day_intervals(self, sy: SchoolYear):
        sy_year = int(sy.year.split("-")[1])
        c = calmod.Calendar()
        fathers_day = None
        sunday_count = 0
        for day in c.itermonthdays2(sy_year, 6):
            if day[0] != 0 and day[1] == 6:
                sunday_count += 1
                if sunday_count == 3:
                    fathers_day = date(sy_year, 6, day[0])
                    break
        if not fathers_day:
            return []
        # §153.314: Dad gets Father's Day regardless of school year
        fri = fathers_day - timedelta(days=2)
        return [CustodyInterval(fri, fathers_day, "dad", "fathers_day")]

    def _mothers_day_intervals(self, sy: SchoolYear):
        sy_year = int(sy.year.split("-")[1])
        c = calmod.Calendar()
        mothers_day = None
        sunday_count = 0
        for day in c.itermonthdays2(sy_year, 5):
            if day[0] != 0 and day[1] == 6:
                sunday_count += 1
                if sunday_count == 2:
                    mothers_day = date(sy_year, 5, day[0])
                    break
        if not mothers_day:
            return []
        school_start = date.fromisoformat(sy.start)
        school_end = date.fromisoformat(sy.end)
        if not (school_start <= mothers_day <= school_end):
            return []
        fri = mothers_day - timedelta(days=2)
        return [CustodyInterval(fri, mothers_day, "mom", "mothers_day")]

    def _noschool_intervals(self, sy: SchoolYear, exclusions: set = None):
        exclusions = exclusions or set()
        break_dates = set()
        for br in sy.breaks.values():
            d = date.fromisoformat(br.start)
            end = date.fromisoformat(br.end)
            while d <= end:
                break_dates.add(d)
                d += timedelta(days=1)
        standalone = []
        for nd in sy.noschool_days:
            nd_date = date.fromisoformat(nd.date)
            if nd_date not in break_dates and nd_date not in exclusions:
                standalone.append(nd_date)
        if not standalone:
            return []
        standalone.sort()
        intervals = []
        group_start = group_end = standalone[0]
        ns_rules = self.rules.get("noschool_days", {})
        custodian = ns_rules.get("odd_year_parent" if self._is_odd_year(group_start) else "even_year_parent", "dad")
        for d in standalone[1:]:
            if d == group_end + timedelta(days=1):
                group_end = d
            else:
                intervals.append(CustodyInterval(group_start, group_end, custodian, "noschool_day"))
                group_start = group_end = d
                custodian = ns_rules.get("odd_year_parent" if self._is_odd_year(group_start) else "even_year_parent", "dad")
        intervals.append(CustodyInterval(group_start, group_end, custodian, "noschool_day"))
        return intervals

    # ── Regular school day intervals ─────────────────────────────────────────

    def _regular_school_intervals(self, sy: SchoolYear, special_dates: set = None):
        """
        Regular school days (Mon-Fri, no holidays/breaks).
        Reads weekend pattern and Thursday rule from custody_rules JSON.
        ESPO & SPO: 1st/3rd/5th Friday weekends, with Thursday for ESPO
        """
        school_start = date.fromisoformat(sy.start)
        school_end = date.fromisoformat(sy.end)
        special_dates = special_dates or set()
        for br in sy.breaks.values():
            d = date.fromisoformat(br.start)
            end = date.fromisoformat(br.end)
            while d <= end:
                special_dates.add(d)
                d += timedelta(days=1)

        weekend_rule = self.rules.get("weekend", {})
        pattern = weekend_rule.get("pattern", "1st_3rd_5th_friday")
        weekend_parent = weekend_rule.get("parent", "dad")

        intervals = []
        d = school_start
        while d <= school_end:
            if d not in special_dates and d.weekday() < 5:
                intervals.append(CustodyInterval(d, d, "mom", "regular_school_day"))
            d += timedelta(days=1)
        return intervals

    # ── Weekend / Thursday intervals ──────────────────────────────────────────

    def _weekend_thursday_intervals(self, sy: SchoolYear, special_dates: set = None):
        """
        Weekend (Fri-Mon or 1st/3rd/5th Sat-Sun) and Thursday intervals.
        Pattern is read from custody_rules JSON.
        """
        school_start = date.fromisoformat(sy.start)
        school_end = date.fromisoformat(sy.end)
        special_dates = special_dates or set()
        for br in sy.breaks.values():
            d = date.fromisoformat(br.start)
            end_d = date.fromisoformat(br.end)
            while d <= end_d:
                special_dates.add(d)
                d += timedelta(days=1)

        weekend_rule = self.rules.get("weekend", {})
        thursday_rule = self.rules.get("thursday", {})
        pattern = weekend_rule.get("pattern", "1st_3rd_5th_friday")
        weekend_parent = weekend_rule.get("parent", "dad")
        thursday_parent = thursday_rule.get("parent", "dad")


        intervals = []
        d_iter = school_start
        while d_iter <= school_end:
            year = d_iter.year
            month = d_iter.month
            last_day = calmod.monthrange(year, month)[1]

            # Both ESPO and SPO: 1st/3rd/5th Friday weekends (per Texas §153.312/153.317)
            # ESPO adds Thursday overnight; SPO may or may not have Thursday per agreement
            if pattern == "1st_3rd_5th_friday":
                # Thursdays
                for day in range(1, last_day + 1):
                    thursday = date(year, month, day)
                    if thursday.weekday() == 3 and school_start <= thursday <= school_end and thursday not in special_dates:
                        intervals.append(CustodyInterval(thursday, thursday, thursday_parent, "espo_thursday"))
                # 1st, 3rd, 5th Friday weekends (Fri → Sun)
                fridays = []
                for day in range(1, last_day + 1):
                    fri = date(year, month, day)
                    if fri.weekday() == 4 and school_start <= fri <= school_end:
                        fridays.append(fri)
                for fri_idx in [0, 2, 4]:
                    if fri_idx < len(fridays):
                        fri = fridays[fri_idx]
                        sat = fri + timedelta(days=1)
                        sun = fri + timedelta(days=2)
                        if fri in special_dates or sat in special_dates or sun in special_dates:
                            continue
                        intervals.append(CustodyInterval(fri, sun, weekend_parent, "espo_weekend"))

            # Move to next month
            if month == 12:
                d_iter = date(year + 1, 1, 1)
            else:
                d_iter = date(year, month + 1, 1)

        return intervals

    # ── Master generator ────────────────────────────────────────────────────

    def generate(self) -> IntervalList:
        result = IntervalList()
        for sy in self.calendar.school_years:
            holiday_dates = set()
            for iv in self._fathers_day_intervals(sy) + self._mothers_day_intervals(sy):
                d = iv.start
                while d <= iv.end:
                    holiday_dates.add(d)
                    d += timedelta(days=1)

            result.extend(self._fathers_day_intervals(sy))
            result.extend(self._mothers_day_intervals(sy))
            result.extend(self._thanksgiving_intervals(sy))
            result.extend(self._christmas_intervals(sy))
            result.extend(self._spring_break_intervals(sy))
            result.extend(self._summer_intervals(sy, holiday_dates))

            # ESPO/SPO weekends and Thursdays (excluding holiday dates)
            wt_intervals = self._weekend_thursday_intervals(sy, holiday_dates)
            wt_dates = set()
            for iv in wt_intervals:
                d = iv.start
                while d <= iv.end:
                    wt_dates.add(d)
                    d += timedelta(days=1)
            result.extend(wt_intervals)

            result.extend(self._noschool_intervals(sy, wt_dates))

            special = set(holiday_dates)
            special.update(wt_dates)
            special.update(self._no_school_dates)
            result.extend(self._regular_school_intervals(sy, special))

        return result


# ─── Loader ────────────────────────────────────────────────────────────────

def load_calendar(path: str) -> StandardCalendar:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    calendar = StandardCalendar(
        district=data["district"],
        source=data.get("source", ""),
        collected_at=data.get("collected_at", ""),
        default_mode=data.get("default_mode", "espo"),
        custody_rules=data.get("custody_rules", {}),
    )

    for sy_data in data.get("schoolYears", []):
        breaks = {}
        for key, br in sy_data.get("breaks", {}).items():
            breaks[key] = SchoolBreak(
                start=br["start"],
                end=br["end"],
                label=br.get("label", {"en": key, "cn": key})
            )
        noschool = [
            NoSchoolDay(date=nd["date"], label=nd.get("label", {"en": nd["date"], "cn": nd["date"]}))
            for nd in sy_data.get("noschool_days", [])
        ]
        calendar.school_years.append(SchoolYear(
            year=sy_data["year"],
            start=sy_data["start"],
            end=sy_data["end"],
            breaks=breaks,
            noschool_days=noschool,
        ))

    return calendar


def save_intervals(intervals: IntervalList, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"count": len(intervals), "intervals": intervals.dump()}, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    cal = load_calendar(os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                     "data", "processed", "rrisd_standard_calendar.json"))
    gen = CustodyIntervalGenerator(cal)
    ivs = gen.generate()
    print(f"Generated {len(ivs)} intervals ({gen.mode})")
    errors = ivs.verify_no_overlaps()
    if errors:
        for e in errors[:5]:
            print("ERROR:", e)
    else:
        print("[OK] No overlaps detected")
