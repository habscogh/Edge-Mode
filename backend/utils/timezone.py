"""
Timezone utilities for Edge Mode
All date/time calculations should use Eastern Time for day boundaries
"""
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo

# App timezone - Eastern Time
APP_TIMEZONE = ZoneInfo("America/New_York")


def get_current_eastern_time() -> datetime:
    """Get current datetime in Eastern Time"""
    return datetime.now(APP_TIMEZONE)


def get_today_eastern() -> date:
    """Get today's date in Eastern Time"""
    return datetime.now(APP_TIMEZONE).date()


def get_today_string() -> str:
    """Get today's date as ISO string in Eastern Time"""
    return get_today_eastern().isoformat()


def parse_date_to_eastern(date_str: str) -> date:
    """Parse a date string and return as date object"""
    return date.fromisoformat(date_str)


def is_same_day_eastern(dt1: datetime, dt2: datetime) -> bool:
    """Check if two datetimes are on the same day in Eastern Time"""
    # Convert both to Eastern Time
    if dt1.tzinfo is None:
        dt1 = dt1.replace(tzinfo=APP_TIMEZONE)
    else:
        dt1 = dt1.astimezone(APP_TIMEZONE)
    
    if dt2.tzinfo is None:
        dt2 = dt2.replace(tzinfo=APP_TIMEZONE)
    else:
        dt2 = dt2.astimezone(APP_TIMEZONE)
    
    return dt1.date() == dt2.date()


def datetime_to_eastern(dt: datetime) -> datetime:
    """Convert a datetime to Eastern Time"""
    if dt.tzinfo is None:
        # Assume UTC if no timezone
        from datetime import timezone
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(APP_TIMEZONE)


def get_eastern_date_from_datetime(dt: datetime) -> str:
    """Get the Eastern Time date string from a datetime"""
    eastern_dt = datetime_to_eastern(dt)
    return eastern_dt.date().isoformat()


def get_eastern_now() -> datetime:
    """Alias for get_current_eastern_time - returns current datetime in Eastern Time"""
    return get_current_eastern_time()
