"""Package for common timezone related method"""
import pytz
from datetime import timedelta

def local_to_utc(date_time):
    if date_time is None:
        return None
    # TODO: get timezone from user.
    localized_time = pytz.timezone('US/Pacific').localize(date_time)
    return (date_time - localized_time.utcoffset()).replace(tzinfo=None)

def utc_to_local(date_time):
    if date_time is None:
        return None
    # TODO: get timezone from user.
    localized_time = pytz.timezone('US/Pacific').localize(date_time)
    local_time = date_time + localized_time.utcoffset()
    if local_time.hour == 23 and local_time.minute == 0 and local_time.second == 0:
        return local_time + timedelta(hours=1)
    else:
        return local_time