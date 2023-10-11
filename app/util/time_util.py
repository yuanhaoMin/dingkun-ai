import logging
import pytz
import time as time_module
from datetime import datetime, time

logger = logging.getLogger(__name__)


def get_current_date_and_day(serve_timezone="Asia/Shanghai"):
    china_tz = pytz.timezone(serve_timezone)
    current_datetime = datetime.now(china_tz)
    current_date = current_datetime.strftime("%Y-%m-%d")
    days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    day_of_week = days[current_datetime.weekday()]
    return current_date, day_of_week


def get_current_datetime(serve_timezone="Asia/Shanghai"):
    china_tz = pytz.timezone(serve_timezone)
    current_datetime = datetime.now(china_tz)
    formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    return formatted_datetime


def get_current_day_times(serve_timezone="Asia/Shanghai"):
    china_tz = pytz.timezone(serve_timezone)
    current_date = datetime.now(china_tz).date()

    start_time = datetime.combine(current_date, time())
    formatted_start_time = start_time.strftime("%Y-%m-%d %H:%M:%S")

    end_time = datetime.combine(current_date, time(hour=23, minute=59, second=59))
    formatted_end_time = end_time.strftime("%Y-%m-%d %H:%M:%S")

    return formatted_start_time, formatted_end_time


def timeit(func):
    def wrapper(*args, **kwargs):
        start_time = time_module.time()
        result = func(*args, **kwargs)
        logger.debug(f"{func.__name__} 耗时: {time_module.time() - start_time}秒")
        return result

    return wrapper
