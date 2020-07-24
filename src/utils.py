from datetime import datetime, timedelta


def get_utc_time(hour, offset):
    datetime_obj = datetime(2020, 5, 20, hour, 0, 0, 0)
    offset = timedelta(minutes=offset)
    utc_time = (datetime_obj + offset).time()
    return utc_time


def get_user_locale_time(utc_time, offset):
    datetime_obj = datetime.combine(datetime.today(), utc_time)
    offset = timedelta(minutes=offset)
    user_locale_time = (datetime_obj - offset).time()
    return user_locale_time
