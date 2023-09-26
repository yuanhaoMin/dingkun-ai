import logging
import pytz
import time
from datetime import datetime

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


def timeit(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        logger.debug(f"{func.__name__} 耗时: {time.time() - start_time}秒")
        return result

    return wrapper
