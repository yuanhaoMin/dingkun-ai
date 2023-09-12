import json


def queryPreviousDatesAlarm(days=7):
    return f"http://127.0.0.1:9000/mock/queryPreviousDatesAlarm?days={days}"


def lastSeasonVisitorTendDatas(months=3):
    return f"http://127.0.0.1:9000/mock/lastSeasonVisitorTendDatas?months={months}"


def patrolTrend(months=1):
    return f"http://127.0.0.1:9000/mock/patrolTrend?months={months}"


def queryInspectionCompletion(region=None):
    return f"http://127.0.0.1:9000/mock/queryInspectionCompletion"



def getInspectionProgress(days=1):
    return f"http://127.0.0.1:9000/mock/getInspectionProgress?days={days}"

def execute_function_from_json(data):
    # 提取function_call字段
    function_call = data["function_call"]

    # 获取函数名和参数
    function_name = function_call["name"]
    arguments = json.loads(function_call["arguments"])

    # 使用getattr获得函数并执行它
    func = globals().get(function_name)
    if func:
        return func(**arguments)
    else:
        raise ValueError(f"Function {function_name} not found")
