import ast
import json
import logging
from app.model.my_sql_table_schema import table_schemas_instance
from app.config.my_sql_db import get_db
from app.model.pydantic_schema.data_visualization_schemas import VisualizeInSVGResponse
from app.util.openai_util import chat_completion_no_functions
from app.util.file_util import create_prompt_from_template_file
from app.util.sql_util import execute_sql
from app.util.time_utll import timeit, get_current_date_and_day
from fastapi import HTTPException

logger = logging.getLogger(__name__)


def visualize_in_svg(input_text: str) -> str:
    # 获取当前日期和星期
    current_date, day_of_week = get_current_date_and_day()

    # 第一步：自然语言转sql
    try:
        sql_query = natural_language_to_sql(
            input_text, table_schemas_instance.get_schemas(), current_date, day_of_week
        )
    except Exception as e:
        # 处理自然语言转SQL的错误
        raise HTTPException(
            status_code=500,
            detail=f"Error in converting natural language to SQL: {e}",
        )

    # 第二步：sql查询数据
    try:
        query_result = execute_sql_query(sql_query)
    except Exception as e:
        # 处理执行SQL查询的错误
        raise HTTPException(
            status_code=500,
            detail=f"Error in executing SQL query: {e}",
        )
    # 为AI提供的数据限制大小, 如5条
    sample_data = query_result[:5]

    # 第三步：数据通过ai分析转成可运行代码
    try:
        visualization_info_str = generate_code_for_svg(
            input_text, sample_data, current_date, day_of_week
        )
        visualization_info = json.loads(visualization_info_str)

        runnable_code = visualization_info["code"]
    except Exception as e:
        # 处理AI分析的错误
        raise HTTPException(
            status_code=500,
            detail=f"Error in code generation for svg: {e}",
        )

    # 第四步：运行代码获取svg数据
    try:
        svg_data = get_svg_from_code_execution(runnable_code, query_result)
    except Exception as e:
        # 处理运行代码获取SVG的错误
        raise HTTPException(
            status_code=500,
            detail=f"Error in get svg from code execution: {e}",
        )
    # 将SVG数据和状态代码包装为JSON对象并返回
    return VisualizeInSVGResponse(svg_data)


@timeit
def natural_language_to_sql(
    user_message: str, table_schema: str, current_date: str, day_of_week: str
) -> str:
    # 使用提示词模板并替换其中的内容
    replacements = {
        "table_schema:": table_schema,
        "current_date:": current_date,
        "day_of_week:": day_of_week,
    }
    system_message = create_prompt_from_template_file(
        filename="sql_generator_prompt", replacements=replacements
    )
    # 构造与AI对话的消息列表
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message},
    ]
    return chat_completion_no_functions(messages)


@timeit
def execute_sql_query(sql_query: str) -> list:
    db = next(get_db())  # 获取数据库会话
    try:
        results = execute_sql(db, sql_query)
        return results
    finally:
        db.close()


@timeit
def generate_code_for_svg(
    input_text: str, query_result: dict, current_date: str, day_of_week: str
) -> str:
    # 使用提示词模板并替换其中的内容
    replacements = {
        "current_date": current_date,  # 使用Python的date.today()获取今天的日期
        "day_of_week": day_of_week,  # 使用strftime获取当前的星期
    }
    prompt = create_prompt_from_template_file(
        filename="data_visualization_code_generator_prompt", replacements=replacements
    )

    # 构造与AI对话的消息列表
    messages = [
        {"role": "system", "content": prompt},
        {
            "role": "user",
            "content": f"Question:\n{input_text}\n\nquery_result_sample:\n{query_result}",
        },
    ]

    # 使用OpenAI API获取可运行的代码
    return chat_completion_no_functions(messages)


@timeit
def get_svg_from_code_execution(code: str, query_result: list) -> str:
    # 检查代码中的语法错误
    ast.parse(code)
    # 运行代码
    exec_env = {"query_result": query_result}  # 将query_result添加到执行环境中
    exec(code, exec_env)  # 在隔离的命名空间中执行代码
    svg_data = exec_env.get("svg_data")  # 代码执行后会在svg_data变量中存放SVG数据
    if svg_data is None:
        raise ValueError("The code did not produce the expected SVG data.")
    return svg_data
