import asyncio
import json
from app.constant.function import data_visualization_functions
from app.constant.json import data_visualization_jsons
from app.util.time_utll import get_current_date_and_day
from app.util.openai_util import (
    chat_completion_with_functions,
    chat_completion_no_functions,
)
from concurrent.futures import ThreadPoolExecutor


async def get_chart_and_function(user_message) -> tuple:
    determine_function_call_messages = create_determine_function_call_messages(
        user_message
    )
    determine_chart_config_messages = create_chart_config_messages(
        user_message, data_visualization_jsons.chart
    )

    (
        function_call_response,
        chart_config_response,
    ) = await run_async_tasks(
        [
            (
                chat_completion_with_functions,
                [
                    determine_function_call_messages,
                    data_visualization_functions.front_end_functions,
                ],
            ),
            (chat_completion_no_functions, [determine_chart_config_messages]),
        ]
    )

    # 检查chat_response是否是预期的HTTP响应对象
    if isinstance(function_call_response, Exception):
        raise function_call_response  # 或者返回一个默认的结果
    chart_config = process_bullet_chart(chart_config_response)
    assistant_message = function_call_response.json()["choices"][0]["message"]
    function_call = assistant_message.get("function_call", {})
    return (chart_config, function_call)


def create_determine_function_call_messages(user_message):
    current_date, day_of_week = get_current_date_and_day()
    system_message = f"You are a helpful assistant. Determine the most likely functions to be called from the requirements given by the user, and infer the appropriate parameters.\nToday is {day_of_week}, {current_date}."
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message},
    ]
    return messages


def create_chart_config_messages(user_message, chart_json):
    current_date, day_of_week = get_current_date_and_day()
    system_message = f"""
        You are a helpful assistant. Determine the most appropriate chart type and parameters in json based on the user's request and following chart information:
        ```
        {chart_json}
        ```
        Strictly answer in the following json format:
        ## FORMAT:
        {{
            "chart_name": "<String>",
            "title": {{
                "visible": true,
                "text": "<Title Text>"
            }},
            "description": {{
                "text": "<Description Text>"
            }},
            "legend": {{
                "flipPage": false
            }},
            "xAxis": {{
                "title": {{
                    "visible": true,
                    "text": "<X-axis Title>"
                }}
            }},
            "yAxis": {{
                "title": {{
                    "visible": true,
                    "text": "<Y-axis Title>"
                }}
            }},
            "color": ["<Color Code>"]
        }}
        If the identified chart type is Bullet, follow this FORMAT:
        ## FORMAT (Bullet):
        {{
            "chart_name": "<String>",
            "color": {{
                "range": ["<Color Code>"], 
                "measure": ["<Color Code>"],
                "target": "<Color Code>"
            }},
            "label": {{
                "measure": {{
                    "position": "<Position>",
                    "style": {{
                        "fill": "<Color Fill>"
                    }}
                }}
            }},
            "xAxis": {{
                "line": null
            }},
            "yAxis": false,
            "legend": {{
                "custom": true,
                "position": "bottom",
                "items": [
                    {{
                        "value": "<Value 1>",
                        "name": "<Name 1>",
                        "marker": {{
                            "symbol": "<Symbol>",
                            "style": {{
                                "fill": "<Color Code>",
                                "r": 5
                            }}
                        }}
                    }},
                    {{
                        "value": "<Value 2>",
                        "name": "<Name 2>",
                        "marker": {{
                            "symbol": "<Symbol>",
                            "style": {{
                                "fill": "<Color Code>",
                                "r": 5
                            }}
                        }}
                    }}
                ]
            }}
        }}
        Today is {day_of_week}, {current_date}. Strictly answer in the above json format and do not say other words!
        """
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message},
    ]
    return messages


async def run_async_tasks(tasks):
    async def run_async(func, *args):
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            return await loop.run_in_executor(executor, func, *args)

    return await asyncio.gather(*[run_async(task[0], *task[1]) for task in tasks])


def process_bullet_chart(chart_data):
    """
    Process the chart data for Bullet charts.

    :param chart_data: The raw chart data to process.
    :return: Processed chart data.
    """
    try:
        # 尝试将输入数据从字符串解析为JSON对象
        parsed_data = json.loads(chart_data)
    except json.JSONDecodeError:
        # 如果解析失败，则直接返回原始数据
        return chart_data

    # 判断chart_name是否为Bullet
    if parsed_data.get("chart_name") == "Bullet":
        # 在顶层添加额外的键值对
        additional_fields = {
            "measureField": "measures",
            "rangeField": "ranges",
            "targetField": "target",
            "xField": "title",
        }
        parsed_data.update(additional_fields)
    return parsed_data
