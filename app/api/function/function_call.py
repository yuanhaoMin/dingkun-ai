import json


def queryPreviousDatesAlarm(days=7):
    return json.dumps({"result": "https://gw.alipayobjects.com/os/bmw-prod/1d565782-dde4-4bb6-8946-ea6a38ccf184.json"})


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


# 你的json数据
data = {
    "function_call": {
        "name": "queryPreviousDatesAlarm",
        "arguments": "{\n  \"days\": 90\n}"
    },
    "chart_info": "{\n  \"chart_name\": \"Column\",\n  \"dataPres\": [\n    {\n      \"minQty\": 1,\n      \"maxQty\": 2,\n      \"fieldConditions\": [\"Nominal\", \"Ordinal\"]\n    },\n    {\n      \"minQty\": 1,\n      \"maxQty\": 1,\n      \"fieldConditions\": [\"Interval\"]\n    }\n  ]\n}"
}

result = execute_function_from_json(data)
print(result)
