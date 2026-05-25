import csv
from datetime import date, timedelta, datetime
import re

PRAYER_TIMES = {}

JUMUAH_ALIASES = frozenset([
    "juma", "jumma", "jummah", "jumuah", "jumu'ah", "jum'uah", "jum'ah",
    "friday prayer", "friday salah", "friday salat", "friday namaz",
    "friday khutba", "friday khutbah",
])

def is_jumuah_question(msg: str) -> bool:
    s = msg.lower()
    if any(alias in s for alias in JUMUAH_ALIASES):
        return True
    if "friday" in s:
        return any(w in s for w in ["prayer", "salah", "salat", "namaz", "khutba", "khutbah", "time", "when", "where"])
    return False

JUMUAH_SCHEDULE = (
    "Jumu'ah at Cambourne Crescent (verify at cambournecrescent.org):\n"
    "Please check the website or contact us for current Jumu'ah times."
)

ALL_PRAYER_TRIGGERS = [
    "all prayers", "prayer times", "prayer timings", "prayer schedule",
    "today's prayers", "prayers today", "prayers for today",
    "prayers for tomorrow", "prayers tomorrow",
    "prayers on ", "prayers for ",
    "namaz times", "namaz timings", "namaz schedule",
    "salah times", "salah timings", "salah schedule",
    "daily prayers", "5 prayers", "five prayers",
]

def load_prayer_times_csv(path="kb/prayer_times_cambourne.csv"):
    global PRAYER_TIMES
    PRAYER_TIMES = {}
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            PRAYER_TIMES[row["date"]] = {k.lower(): v for k, v in row.items()}


def _parse_date_from_msg(msg: str) -> str | None:
    """Returns an ISO date string parsed from msg, or None if not found."""
    parsed_date = None

    hyphen_match = re.search(r'(\d{1,2})-(\d{1,2})(?:-(\d{4}))?', msg)
    if hyphen_match:
        a, b, year = hyphen_match.groups()
        a, b = int(a), int(b)
        year = int(year) if year else date.today().year
        day, month = 0, 0
        if a > 12 and b <= 12:
            day, month = a, b
        elif b > 12 and a <= 12:
            day, month = b, a
        else:
            try:
                datetime(year, b, a)
                day, month = a, b
            except ValueError:
                try:
                    datetime(year, a, b)
                    day, month = b, a
                except ValueError:
                    pass
        if 1 <= day <= 31 and 1 <= month <= 12:
            try:
                parsed_date = datetime(year, month, day).date().isoformat()
            except ValueError:
                pass

    if not parsed_date:
        cleaned_msg = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', msg)
        day_month_match = re.search(r'(\d{1,2})\s+(\w+)(?:\s+(\d{4}))?', cleaned_msg)
        if day_month_match:
            day_str, month_str, year_str = day_month_match.groups()
            day = int(day_str)
            year = int(year_str) if year_str else date.today().year
            try:
                month = datetime.strptime(month_str, "%B").month
                parsed_date = datetime(year, month, day).date().isoformat()
            except ValueError:
                try:
                    month = datetime.strptime(month_str, "%b").month
                    parsed_date = datetime(year, month, day).date().isoformat()
                except ValueError:
                    pass
        if not parsed_date:
            month_day_match = re.search(r'(\w+)\s+(\d{1,2})(?:\s+(\d{4}))?', cleaned_msg)
            if month_day_match:
                month_str, day_str, year_str = month_day_match.groups()
                day = int(day_str)
                year = int(year_str) if year_str else date.today().year
                try:
                    month = datetime.strptime(month_str, "%B").month
                    parsed_date = datetime(year, month, day).date().isoformat()
                except ValueError:
                    try:
                        month = datetime.strptime(month_str, "%b").month
                        parsed_date = datetime(year, month, day).date().isoformat()
                    except ValueError:
                        pass

    if not parsed_date:
        day_match = re.search(r'\b(\d{1,2})\b', msg)
        if day_match:
            day = int(day_match.group(1))
            if 1 <= day <= 31:
                try:
                    parsed_date = datetime(date.today().year, date.today().month, day).date().isoformat()
                except ValueError:
                    pass

    if not parsed_date:
        day_name_map = {
            "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
            "friday": 4, "saturday": 5, "sunday": 6,
        }
        for name, weekday in day_name_map.items():
            if name in msg:
                today_d = date.today()
                days_ahead = (weekday - today_d.weekday()) % 7
                if "next" in msg and days_ahead == 0:
                    days_ahead = 7
                parsed_date = (today_d + timedelta(days=days_ahead)).isoformat()
                break

    return parsed_date


_SINGLE_PRAYER_TERMS = frozenset([
    "fajr", "fajar", "fajir", "dhuhr", "zuhr", "dhuhar", "zuhar",
    "asr", "asar", "maghrib", "magrib", "iftar", "aftar", "iftari", "aftari",
    "isha", "ishaa", "ishah", "esha",
])

_DAY_NAMES = frozenset(["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"])


def check_all_prayers_request(msg: str) -> str | None:
    """Returns all 5 daily prayer times for a date. Includes Jumu'ah info if the date is a Friday."""
    s = msg.lower()

    if any(t in s for t in _SINGLE_PRAYER_TERMS):
        return None

    triggered = any(t in s for t in ALL_PRAYER_TRIGGERS)
    if not triggered:
        has_day = any(d in s for d in _DAY_NAMES)
        has_prayer_word = any(w in s for w in ["prayer", "prayers", "namaz", "salah"])
        triggered = has_day and has_prayer_word
    if not triggered:
        return None

    today = date.today()
    tomorrow = today + timedelta(days=1)
    parsed_date = _parse_date_from_msg(s)
    d_str = parsed_date if parsed_date else (tomorrow.isoformat() if "tomorrow" in s else today.isoformat())

    row = PRAYER_TIMES.get(d_str)
    if not row:
        return f"Prayer times are not available for {d_str}. Please check cambournecrescent.org for the latest times."

    d_date = date.fromisoformat(d_str)
    header = d_date.strftime("%A, %-d %B %Y")
    lines = [f"Prayer times for {header}:"]

    for label, adhan_col, iqamah_col in [
        ("Fajr",    "fajr_start",    "fajr_jamaat"),
        ("Dhuhr",   "dhuhr_start",   "dhuhr_jamaat"),
        ("Asr",     "asr_start",     "asr_jamaat"),
        ("Maghrib", "maghrib_start", "maghrib_jamaat"),
        ("Isha",    "isha_start",    "isha_jamaat"),
    ]:
        adhan = row.get(adhan_col, "")
        iqamah = row.get(iqamah_col, "")
        if adhan:
            lines.append(f"  {label}: Adhan {adhan}, Iqamah {iqamah}" if iqamah else f"  {label}: {adhan}")

    if d_date.weekday() == 4:  # Friday
        if d_date < today:
            lines.append("\nJumu'ah: Timings not available for past dates.")
        elif (d_date - today).days <= 6:
            lines.append(f"\n{JUMUAH_SCHEDULE}")
        else:
            lines.append("\nJumu'ah: Timings will be shared once published.")

    return "\n".join(lines)


def check_prayer_time_shortcuts(msg: str):
    msg = msg.lower()
    today = date.today().isoformat()
    tomorrow = (date.today() + timedelta(days=1)).isoformat()

    parsed_date = _parse_date_from_msg(msg)

    mapping = {
        "fajr": "fajr_start",
        "fajar": "fajr_start",
        "fajir": "fajr_start",
        "dhuhr": "dhuhr_start",
        "dhuhar": "dhuhr_start",
        "zuhar": "dhuhr_start",
        "zuhr": "dhuhr_start",
        "asr": "asr_start",
        "asar": "asr_start",
        "maghrib": "maghrib_start",
        "magrib": "maghrib_start",
        "iftar": "maghrib_start",
        "aftar": "maghrib_start",
        "iftari": "maghrib_start",
        "aftari": "maghrib_start",
        "isha": "isha_start",
        "isha'a": "isha_start",
        "ishaa": "isha_start",
        "ishah": "isha_start",
        "esha": "isha_start",
    }

    matched_term = next((term for term in mapping if term in msg), None)
    if not matched_term:
        return None

    d = parsed_date if parsed_date else (tomorrow if "tomorrow" in msg else today)
    row = PRAYER_TIMES.get(d)
    if not row:
        return None

    key = mapping[matched_term]
    adhan = row.get(key)
    if not adhan:
        return None

    iqamah = row.get(key.replace("_start", "_jamaat"), "")

    label = "Iftar (Maghrib)" if matched_term == "iftar" else matched_term.capitalize()
    day_desc = f"on {d}" if parsed_date else ("tomorrow" if d == tomorrow else "today")
    time_str = f"Adhan {adhan}, Iqamah {iqamah}" if iqamah else adhan
    return f"{label} {day_desc}: {time_str}."
