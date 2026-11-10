"""Date and time resolution utilities for natural language query ranges."""

from datetime import date, datetime, timedelta, timezone
from typing import Tuple


def get_relative_date_range(days: int) -> Tuple[datetime, datetime]:
    """
    Return a tuple of (start_datetime, end_datetime) for a window of `days` back from now.
    Example: days=90 returns (now - 90 days, now).
    """
    now = datetime.now(timezone.utc)
    start = now - timedelta(days=days)
    return start, now


def get_expiry_window(days: int) -> Tuple[date, date]:
    """
    Return a tuple of (today, today + days) for expiration window queries.
    Example: days=30 returns dates between today and today + 30 days.
    """
    today = date.today()
    future = today + timedelta(days=days)
    return today, future
