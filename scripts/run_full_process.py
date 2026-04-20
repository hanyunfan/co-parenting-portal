import os, sys, json, argparse
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from geocode_district import geocode, search_district, cache_district
from calendar_fetcher_parser import DataNormalizer
from custody_interval_calculator import CustodyIntervalGenerator, load_calendar, save_intervals
from static_web_generator import HTMLBuilder

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
CONFIG_DIR = os.path.join(PROJECT_ROOT, "config")
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")


def load_default_address():
    path = os.path.join(CONFIG_DIR, "default_address.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)["address"]


def find_existing_calendar(district):
    processed = os.path.join(DATA_DIR, "processed")
    if not os.path.exists(processed):
        return None
    dl = district.lower().replace(" ", "_")
    for fname in os.listdir(processed):
        if dl in fname.lower() and fname.endswith(".json") and "interval" not in fname:
            return os.path.join(processed, fname)
    return None


def build_espo_calendar():
    normalizer = DataNormalizer("RRISD")
    normalizer.set_source("RRISD official calendar 2025-26 / 2026-27")

    normalizer.add_school_year(
        year="2025-2026",
        start="2025-08-13",
        end="2026-05-21",
        breaks={
            "thanksgiving": {
                "start": "2025-11-24", "end": "2025-11-28",
                "label": {"en": "Thanksgiving Break", "cn": "感恩节假期"}
            },
            "christmas": {
                "start": "2025-12-19", "end": "2026-01-05",
                "label": {"en": "Christmas Break", "cn": "圣诞假期"}
            },
            "spring": {
                "start": "2026-03-16", "end": "2026-03-20",
                "label": {"en": "Spring Break", "cn": "春假"}
            },
            "summer": {
                "start": "2026-05-22", "end": "2026-08-11",
                "label": {"en": "Summer Break", "cn": "暑假"}
            }
        },
        noschool_days=[
            {"date": "2025-09-01", "label": {"en": "Labor Day", "cn": "劳动节"}},
            {"date": "2025-09-22", "label": {"en": "Rosh Hashanah (Student & Staff Holiday)", "cn": "犹太新年"}},
            {"date": "2025-09-23", "label": {"en": "Rosh Hashanah (Student & Staff Holiday)", "cn": "犹太新年"}},
            {"date": "2025-10-13", "label": {"en": "Indigenous Peoples' Day / Columbus Day (Student Holiday)", "cn": "原住民日/哥伦布日"}},
            {"date": "2025-10-20", "label": {"en": "Diwali (Student & Staff Holiday)", "cn": "排灯节"}},
            {"date": "2025-11-07", "label": {"en": "Staff Dev / Student Holiday", "cn": "教师培训/学生假日"}},
            {"date": "2026-01-05", "label": {"en": "Martin Luther King Jr. Day (Student & Staff Holiday)", "cn": "马丁路德金日"}},
            {"date": "2026-02-16", "label": {"en": "Presidents' Day (Student & Staff Holiday)", "cn": "总统日"}},
            {"date": "2026-02-17", "label": {"en": "Lunar New Year (Student Holiday/Staff Dev)", "cn": "农历新年"}},
            {"date": "2026-04-03", "label": {"en": "Good Friday (Student & Staff Holiday)", "cn": "耶稣受难日"}},
            {"date": "2026-06-19", "label": {"en": "Juneteenth (Student Holiday)", "cn": "六月节"}},
        ]
    )

    normalizer.add_school_year(
        year="2026-2027",
        start="2026-08-18",
        end="2027-05-27",
        breaks={
            "thanksgiving": {
                "start": "2026-11-23", "end": "2026-11-27",
                "label": {"en": "Thanksgiving Break", "cn": "感恩节假期"}
            },
            "christmas": {
                "start": "2026-12-18", "end": "2027-01-05",
                "label": {"en": "Christmas Break", "cn": "圣诞假期"}
            },
            "spring": {
                "start": "2027-03-15", "end": "2027-03-19",
                "label": {"en": "Spring Break", "cn": "春假"}
            },
            "summer": {
                "start": "2027-05-28", "end": "2027-08-16",
                "label": {"en": "Summer Break", "cn": "暑假"}
            }
        },
        noschool_days=[
            {"date": "2026-09-04", "label": {"en": "Staff Dev / Student Holiday", "cn": "教师培训/学生假日"}},
            {"date": "2026-09-07", "label": {"en": "Labor Day (Student & Staff Holiday)", "cn": "劳动节"}},
            {"date": "2026-09-21", "label": {"en": "Yom Kippur (Student Holiday/Staff Dev)", "cn": "赎罪日"}},
            {"date": "2026-10-12", "label": {"en": "Indigenous Peoples' Day / Columbus Day (Student Holiday)", "cn": "原住民日/哥伦布日"}},
            {"date": "2026-10-19", "label": {"en": "Student & Staff Holiday", "cn": "学生/教师假日"}},
            {"date": "2026-11-09", "label": {"en": "Diwali (Student Holiday/Staff Dev)", "cn": "排灯节"}},
            {"date": "2027-01-18", "label": {"en": "Martin Luther King Jr. Day (Student & Staff Holiday)", "cn": "马丁路德金日"}},
            {"date": "2027-02-05", "label": {"en": "Lunar New Year (Student Holiday/Staff Dev)", "cn": "农历新年"}},
            {"date": "2027-02-15", "label": {"en": "Presidents' Day (Student & Staff Holiday)", "cn": "总统日"}},
            {"date": "2027-03-10", "label": {"en": "Eid al-Fitr (Student Holiday/Staff Dev)", "cn": "开斋节"}},
            {"date": "2027-03-26", "label": {"en": "Good Friday (Student & Staff Holiday)", "cn": "耶稣受难日"}},
            {"date": "2027-05-31", "label": {"en": "Memorial Day (Staff Holiday/Student Holiday)", "cn": "阵亡将士纪念日"}},
            {"date": "2027-06-19", "label": {"en": "Juneteenth (Student Holiday)", "cn": "六月节"}},
        ]
    )

    errors = normalizer.validate()
    if errors:
        print("Validation errors:", errors)
    else:
        print("[OK] Calendar data valid")

    saved = normalizer.save()

    # Append custody_rules to the saved JSON
    # Per Texas §153.312/153.314/153.317:
    # - Both ESPO and SPO: 1st, 3rd, 5th Friday weekends (Dad)
    # - ESPO adds Thursday overnight; SPO per agreement
    # - Thanksgiving/Christmas/Spring: alternating by calendar year
    # - Christmas split: Dec 28 noon; odd year Dad first half, even year Mom first half
    custody_rules = {
        "espo": {
            "weekend": {"pattern": "1st_3rd_5th_friday", "parent": "dad"},
            "thursday": {"parent": "dad"},
            "holidays": {
                "thanksgiving": {"odd_year_parent": "dad", "even_year_parent": "mom"},
                "christmas": {"split": "first_second_half", "odd_year_parent": "dad", "even_year_parent": "mom", "split_day": 28},
                "spring_break": {"odd_year_parent": "mom", "even_year_parent": "dad"},
            },
            "summer": {"parent": "dad", "default_30_days": "july_1_30"},
            "noschool_days": {"odd_year_parent": "dad", "even_year_parent": "mom"},
        },
        "spo": {
            "weekend": {"pattern": "1st_3rd_5th_friday", "parent": "dad"},
            "thursday": {"parent": "dad"},
            "holidays": {
                "thanksgiving": {"odd_year_parent": "dad", "even_year_parent": "mom"},
                "christmas": {"split": "first_second_half", "odd_year_parent": "dad", "even_year_parent": "mom", "split_day": 28},
                "spring_break": {"odd_year_parent": "mom", "even_year_parent": "dad"},
            },
            "summer": {"parent": "dad", "default_30_days": "july_1_30"},
            "noschool_days": {"odd_year_parent": "dad", "even_year_parent": "mom"},
        },
    }
    with open(saved, "r+", encoding="utf-8") as f:
        data = json.load(f)
        data["custody_rules"] = custody_rules
        f.seek(0)
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.truncate()

    return saved


def main():
    parser = argparse.ArgumentParser(description="Custody calendar pipeline")
    parser.add_argument("--address", default=None)
    parser.add_argument("--district", default="RRISD")
    parser.add_argument("--mode", default="espo", choices=["espo", "spo"])
    args = parser.parse_args()

    address = args.address or load_default_address()
    print(f"[1] Address: {address}")

    print(f"[2] Geocoding...")
    geo = geocode(address)
    if geo:
        print(f"    lat={geo.lat:.4f} lon={geo.lon:.4f} city={geo.city}")
    else:
        print("    (geocoding failed)")

    district = args.district
    if geo:
        found, cal_url = search_district(address, geo.city, geo.state, geo.county)
        district = found
        print(f"[3] District: {district} | calendar: {cal_url or 'N/A'}")
        if cal_url:
            cache_district(address, district, cal_url)
    else:
        print(f"[3] District: {district}")

    cal_path = find_existing_calendar(district)
    if not cal_path:
        print(f"[4] Building calendar for {district}...")
        cal_path = build_espo_calendar()
    else:
        print(f"[4] Using existing: {cal_path}")

    calendar = load_calendar(cal_path)

    print(f"[5] Computing ESPO intervals...")
    gen_espo = CustodyIntervalGenerator(calendar, mode="espo")
    ivs_espo = gen_espo.generate()
    errors = ivs_espo.verify_no_overlaps()
    print(f"    ESPO: {len(ivs_espo)} intervals, {'OVERLAPS: ' + str(errors) if errors else 'OK'}")

    print(f"[5b] Computing SPO intervals...")
    gen_spo = CustodyIntervalGenerator(calendar, mode="spo")
    ivs_spo = gen_spo.generate()
    errors_spo = ivs_spo.verify_no_overlaps()
    print(f"    SPO: {len(ivs_spo)} intervals, {'OVERLAPS: ' + str(errors_spo) if errors_spo else 'OK'}")

    print(f"[6] Generating HTML...")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    html_dest = os.path.join(OUTPUT_DIR, "custody_school_calendar.html")
    HTMLBuilder(district, ivs_espo.dump(), ivs_spo.dump()).build(html_dest)

    print(f"[DONE] {html_dest}")


if __name__ == "__main__":
    main()
