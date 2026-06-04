from zoneinfo import ZoneInfo
from datetime import datetime

JAKARTA_TZ = ZoneInfo('Asia/Jakarta')


def now_jakarta() -> datetime:
    return datetime.now(JAKARTA_TZ)


def utc_to_jakarta(dt: datetime) -> datetime:
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo('UTC'))
    return dt.astimezone(JAKARTA_TZ)


def format_jakarta(dt: datetime, fmt: str = '%d/%m/%Y %H:%M') -> str:
    if dt is None:
        return '-'
    return utc_to_jakarta(dt).strftime(fmt)


def current_year_jakarta() -> int:
    return now_jakarta().year
