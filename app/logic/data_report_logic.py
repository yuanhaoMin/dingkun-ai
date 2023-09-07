from app.api.dependency.database import table_schemas_instance
from app.chain.generator_code_chains import ai_analyze_query_result_to_code_chain
from app.chain.sql_chains import natural_language_to_sql_chain
from app.util.execution_util import run_code_to_get_svg
from app.util.sql_util import get_db, execute_sql
from datetime import datetime
import json
from app.knowledge.api_json import functions
from app.util.openai_util import chat_completion_request, completion
import asyncio
from concurrent.futures import ThreadPoolExecutor
from app.util.time_utll import timeit

current_date = datetime.now().strftime("%Y-%m-%d")
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
today = datetime.today().date()
day_of_week = days[today.weekday()]


def generate_data_report(input_text: str) -> str:
    """
    基于用户输入生成数据报告。

    参数:
    - input_text: 用户提供的自然语言输入。

    返回:
    - SVG数据。
    """

    # 第一步：自然语言转sql
    try:
        sql_query = natural_language_to_sql_chain(
            input_text, table_schemas_instance.get_schemas(), current_date, day_of_week
        )
        print(sql_query)
    except Exception as e:
        # 处理自然语言转SQL的错误
        raise Exception(f"Error in converting natural language to SQL: {str(e)}")

    # 第二步：sql查询数据
    try:
        query_result = execute_sql_query(sql_query)
    except Exception as e:
        # 处理执行SQL查询的错误
        raise Exception(f"Error in executing SQL query: {str(e)}")
        # 为AI提供的数据限制大小
    ai_sample_data = query_result[:5]  # 例如选择前5条数据

    # 第三步：数据通过ai分析转成可运行代码
    try:
        visualization_info_str = ai_analyze_query_result_to_code_chain(
            input_text, ai_sample_data, current_date, day_of_week
        )
        print(visualization_info_str)
        visualization_info = json.loads(visualization_info_str)

        runnable_code = visualization_info["code"]
        description = visualization_info["description"]
        print(description)
        print(runnable_code)
    except Exception as e:
        # 处理AI分析的错误
        raise Exception(f"Error in AI analysis: {str(e)}")

    # 第四步：运行代码获取svg数据
    try:
        svg_data = run_code_to_get_svg(runnable_code, query_result)
    except Exception as e:
        # 处理运行代码获取SVG的错误
        raise Exception(f"Error in generating SVG: {str(e)}")

    # 将SVG数据和状态代码包装为JSON对象并返回
    response_data = {"data": svg_data, "status_code": 200}

    return json.dumps(response_data)


@timeit
def execute_sql_query(sql_query: str) -> list:
    """
    根据提供的SQL查询执行查询并返回结果。

    参数:
    - sql_query: 要执行的SQL查询。

    返回:
    - 查询结果作为字典列表。
    """
    db = next(get_db())  # 获取数据库会话
    try:
        results = execute_sql(db, sql_query)
        return results
    finally:
        db.close()


def create_guidance_message(user_message):
    messages = []
    messages.append({
        "role": "system",
        "content": "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous."
    })
    messages.append({"role": "user", "content": user_message})
    return messages


def create_chart_config_prompt_message(user_message, chart_json):
    prompt = f"""
        Based on the user's request and using the provided chart dictionary:
        ```
        {chart_json}
        ```
        Identify the most appropriate chart type and provide configuration details in the following format:
         ## FORMAT:
        {{
            "chart_name": "<String>",
            "title": {{
                "visible": True,
                "text": "<Title Text>"
            }},
            "description": {{
                "text": "<Description Text>"
            }},
            "legend": {{
                "flipPage": False
            }},
            "xAxis": {{
                "title": {{
                    "visible": True,
                    "text": "<X-axis Title>"
                }}
            }},
            "yAxis": {{
                "title": {{
                    "visible": True,
                    "text": "<Y-axis Title>"
                }}
            }},
            "color": ["<Color Code>"]
        }}
        """
    str_ = 'Must follow the format and not reply to any other words!'
    messages = []
    messages.append({"role": "system", "content": prompt})
    messages.append({"role": "user", "content": user_message + str_})
    return messages


def get_chart_and_function(user_message, chart_json):
    messages = create_guidance_message(user_message)
    messages2 = create_chart_config_prompt_message(user_message, chart_json)

    async def run_async(func, *args):
        with ThreadPoolExecutor() as executor:
            return await asyncio.get_event_loop().run_in_executor(executor, func, *args)

    loop = asyncio.get_event_loop()
    chat_response, completion_response = loop.run_until_complete(
        asyncio.gather(
            run_async(chat_completion_request, messages, functions),
            run_async(completion, messages2)
        )
    )

    assistant_message = chat_response.json()["choices"][0]["message"]

    result = {
        'function_call': assistant_message.get('function_call', {}),
        'chart_info': completion_response
    }

    return result
