import re
from datetime import datetime, timezone, timedelta

__date_rx__ = re.compile(r"^(?P<year>\d{4})-(?P<month>\d\d)-(?P<day>\d\d)[Tt](?P<hour>\d\d):(?P<minute>\d\d):(?P<second>\d\d)(?:\.(?P<sec_frac>\d+))?(?P<offset>(?:[zZ]|(?P<offset_sign>[+-])(?P<offset_hour>\d{2}):(?P<offset_minute>\d{2})))$")

def parse_rfc3339(dt_str: str) -> datetime:
    try:
        result = re.search(__date_rx__, dt_str)

        if result.lastindex < 7 or result.lastindex > 11:
            return None

        sec_frac_int = 0

        sec_frac = result["sec_frac"]
        if sec_frac is not None:
            sec_frac_str = sec_frac[:6] if len(sec_frac) > 6 else sec_frac
            sec_frac_int = int(sec_frac_str)*(10**(6 - len(sec_frac_str)))

        tz = timezone(timedelta())

        if not (result["offset"] == "z" or result["offset"] == "Z"):

            offset_hour = int(result["offset_hour"])
            offset_minute = int(result["offset_minute"])

            if result["offset_sign"] == "-":
                offset_minute *= -1
                offset_hour *= -1
            
            tz = timezone(timedelta(hours=offset_hour, minutes=offset_minute))

        return datetime(
            int(result["year"]),
            int(result["month"]),
            int(result["day"]),
            int(result["hour"]),
            int(result["minute"]),
            int(result["second"]),
            sec_frac_int,
            tz
        )
    except:
        return None
