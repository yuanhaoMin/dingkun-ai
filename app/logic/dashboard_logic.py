import json
import os
from app.constant.schema.dashboard_schemas import (
    information_extraction_schema,
    table_data_time_and_pagination_schema,
)
from app.logic.helper_logic import FILE_PATH
from app.util.embeddings_util import (
    load_situations_embeddings,
    judge_message_category,
    generate_and_save_embeddings,
)
from app.util.openai_util import chat_completion_with_functions
from app.util.time_utll import get_current_date_and_day, get_current_datetime

# 定义文本常量
TEXT_CONSTANTS = {
    "weekly_data": "近一周数据",
    "online_person_details": "在线人员详情",
    "fence_alarm_trend": "告警趋势",
    "central_map": "中心地图",
    "patrol_trend": "巡检趋势",
    "work_card_hat_bracelet_pie_chart": "工牌工帽手环环形图",
    "visitor_number": "访客数量",
    "patrol_task": "巡检任务",
    "alarm_list": "告警列表",
}

# 定义文件路径
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(
    CURRENT_DIR, "..", "constant", "text_constants_embeddings.parquet"
)
# 如果文件不存在，则生成并保存embeddings
if not os.path.exists(FILE_PATH):
    generate_and_save_embeddings(TEXT_CONSTANTS, FILE_PATH)

current_date, day_of_week = get_current_date_and_day()

chart_positions = """
近一周数据:1
在线人员详情:2
告警趋势:3
中心地图:4
巡检趋势:5
工牌工帽手环环形图:6
访客数量:7
巡检任务:8
告警列表:9
"""


def extract_time_and_page_information(query: str) -> dict:
    current_time = get_current_datetime()
    prompt = f"""
        You need to help me find the requirements for the start time, end time, and pagination of the table data that the user needs, 
        with the time being accurate to hours, minutes, and seconds, like that 'YYYY-MM-DD HH:mm:ss'.
        The current time: {current_time}
    """

    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": query},
    ]

    max_retries = 3
    for _ in range(max_retries):
        # 发送请求
        res = chat_completion_with_functions(
            messages,
            functions=table_data_time_and_pagination_schema,
            function_call={"name": "get_table_data_time_and_pagination"},
        )
        if res:
            arguments_data = json.loads(
                res.json()["choices"][0]["message"]["function_call"]["arguments"]
            )
            # 解析arguments中的数据，并根据其存在性决定是否包含在结果中
            result = {
                "start_time": arguments_data.get("start_time", ""),
                "end_time": arguments_data.get("end_time", ""),
                "page": arguments_data.get("page", ""),
                "listRows": arguments_data.get("listRows", ""),
            }

            return result
    return {
        "start_time": "",
        "end_time": "",
        "page": "",
        "listRows": "",
    }

    arguments_data = json.loads(
        res.json()["choices"][0]["message"]["function_call"]["arguments"]
    )

    # 解析arguments中的数据，并根据其存在性决定是否包含在结果中
    result = {
        "start_time": arguments_data.get("start_time", ""),
        "end_time": arguments_data.get("end_time", ""),
        "page": arguments_data.get("page", ""),
        "listRows": arguments_data.get("listRows", ""),
    }

    return result


def extract_chart_information(chart_positions: str, query: str) -> dict:
    # 格式化提示词
    prompt = f'''
    Extract and save the relevant entities mentioned in the following passage together with their properties. 
    Please note that the text to be extracted is often in Chinese and there may be issues with homophones and synonyms. 
    Still, do your best to extract the most likely information.
    Chart positions:
    这是图表对应位置的表
    chart:position
    {chart_positions}
    additional_info = """
    Note:
    3 represents the bottom-left corner.
    4 represents the center area.
    9 represents the bottom-right corner.
    """
    Note  today is: {current_date}, {day_of_week}.
    '''

    # 创建消息列表
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": query},
    ]

    max_retries = 3
    for _ in range(max_retries):
        # 发送请求
        res = chat_completion_with_functions(
            messages,
            functions=information_extraction_schema,
            function_call={"name": "information_extraction"},
        )
        if res:
            arguments_data = json.loads(
                res.json()["choices"][0]["message"]["function_call"]["arguments"]
            )

            # 解析arguments中的数据，并根据其存在性决定是否包含在结果中
            result = {
                "action": arguments_data.get("action", ""),
                "target": arguments_data.get("target", ""),
                "position": arguments_data.get("position", ""),
                "newTarget": arguments_data.get("newTarget", ""),
            }

            return result
    # 如果重试了三次还没有成功，则返回默认的结果
    return {
        "action": "",
        "target": "",
        "position": "",
        "newTarget": "",
    }

    arguments_data = json.loads(
        res.json()["choices"][0]["message"]["function_call"]["arguments"]
    )

    # 解析arguments中的数据，并根据其存在性决定是否包含在结果中
    result = {
        "action": arguments_data.get("action", ""),
        "target": arguments_data.get("target", ""),
        "position": arguments_data.get("position", ""),
        "newTarget": arguments_data.get("newTarget", ""),
    }

    return result


# 定义一个函数来判断与给定常量的相似性
def get_most_similar_constant(
    message, text_constants=TEXT_CONSTANTS, file_path=FILE_PATH
):
    # 加载持久化的embeddings
    situations = load_situations_embeddings(TEXT_CONSTANTS, FILE_PATH)

    # 判断消息与给定常量的相似性
    category = judge_message_category(message, TEXT_CONSTANTS, FILE_PATH)
    return text_constants[category]


def handle_extracted_information(
    chart_positions: str, extracted_info: dict, query: str
) -> dict:
    target = extracted_info.get("target", "")

    if target == "" or target == "chart:position":
        extracted_info["target"] = ""
        return extracted_info

    # 转换 chart_positions 为字典方便查询
    chart_positions_dict = dict(
        [item.split(":") for item in chart_positions.strip().split("\n")]
    )

    # 如果 target 不在 chart_positions 里
    if target not in chart_positions_dict:
        matched_constant = get_most_similar_constant(target)
        extracted_info["matched_constant"] = matched_constant
        target = matched_constant  # 更新 target 为匹配到的常量

    # 针对特定的 target 进行处理
    if target in ["巡检趋势", "访客详情", "告警趋势", "巡检任务", "告警列表"]:
        time_and_page_dict = extract_time_and_page_information(query)
        extracted_info.update(time_and_page_dict)

    return extracted_info
