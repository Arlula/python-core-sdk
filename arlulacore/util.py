import math
import re
import typing
import requests

from datetime import datetime, timezone, timedelta
from arlulacore.exception import ArlulaSessionError

__date_rx__ = re.compile(r"^(?P<year>\d{4})-(?P<month>\d\d)-(?P<day>\d\d)[Tt](?P<hour>\d\d):(?P<minute>\d\d):(?P<second>\d\d)(?:\.(?P<sec_frac>\d+))?(?P<offset>(?:[zZ]|(?P<offset_sign>[+-])(?P<offset_hour>\d{2}):(?P<offset_minute>\d{2})))$")

def remove_none(d: dict) -> dict:
    return {k: v for k, v in d.items() if v is not None}

def get_error(resp: requests.Response):
    return ArlulaSessionError(f"{resp.status_code}: {resp.text}")

def simple_indent(s: str, first_amount: int, following_amount: int) -> str:
    lines = s.splitlines()
    out = [""]*len(lines)

    for i, l in enumerate(lines):
        if i == 0:
            out[i] = first_amount*' ' + l
        else:
            out[i] = following_amount*' ' + l
    return '\n'.join(out) + '\n'

def parse_rfc3339(dt_str: str) -> datetime:
    """
        Parses the provided string as an RFC3339 timestamp. 
        Included as the core python behaviour does not parse RFC3339 timestamps
        correctly and common libraries are massive.
    """
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

def calculate_price(
    bundle_price: int, 
    license_loading_percent: float, 
    license_loading_amount: int,
    cloud_loading_percent: typing.Optional[float] = 0,
    cloud_loading_amount: typing.Optional[int] = 0,
    priority_loading_percent: typing.Optional[float] = 0,
    priority_loading_amount: typing.Optional[int] = 0,
) -> int:
    """
        Calculates the price for purchasing archive and tasking results.
        cloud and priority fields are only required if tasking.
        ***Return value is in US cents, rounded UP to nearest whole dollar.***
    """
    
    percentages = (1 + license_loading_percent/100)
    percentages = percentages + (priority_loading_percent/100)
    percentages = percentages + (cloud_loading_percent/100)
    
    loadings = license_loading_amount
    loadings = loadings + priority_loading_amount
    loadings = loadings + cloud_loading_amount
    
    price = bundle_price * percentages + loadings
    
    return math.ceil(price/100)*100
