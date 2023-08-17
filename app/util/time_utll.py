import time
from datetime import datetime, timedelta


def parse_relative_date(relative_time):
    today = datetime.today()

    if "明天" in relative_time:
        return today + timedelta(days=1)
    elif "今天" in relative_time:
        return today
    elif "后天" in relative_time:
        return today + timedelta(days=2)
    elif "下周五" in relative_time:
        return today + timedelta((4 - today.weekday()) + 7)
    elif "本周六" in relative_time:
        if today.weekday() < 5:  # 如果今天是星期五或之前
            return today + timedelta(days=(5 - today.weekday()))
        else:  # 如果今天是星期六或星期天
            return today + timedelta(days=(5 - today.weekday() + 7))
    # ... 其他相对时间的解析

    return None


def timeit(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        print(f"{func.__name__} 耗时: {time.time() - start_time}秒")
        return result

    return wrapper
