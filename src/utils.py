from datetime import datetime, timedelta


def get_utc_time(hour, offset):
    full_datetime = datetime(2020, 5, 20, hour, 0, 0, 0)
    offset = timedelta(minutes=offset)
    utc_time = (full_datetime + offset).time()
    return utc_time
