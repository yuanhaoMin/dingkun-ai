from app.api.dependency.database import table_schemas_instance
from app.chain.generator_code_chains import ai_analyze_query_result_to_code_chain
from app.chain.sql_chains import natural_language_to_sql_chain
from app.util.execution_util import run_code_to_get_svg
from app.util.sql_util import get_db, execute_sql
from datetime import datetime
import json

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
