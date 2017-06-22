"""Package for common timezone related method"""
import pytz

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
    return date_time + localized_time.utcoffset()