from app.chain.sql_chains import natural_language_to_sql_chain
from app.util.openai_util import completion
from app.util.sql_util import get_db, execute_sql
from app.util.text_util import create_prompt_from_template_file
from datetime import datetime

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
        sql_query = natural_language_to_sql_chain(input_text)
    except Exception as e:
        # 处理自然语言转SQL的错误
        raise Exception(f"Error in converting natural language to SQL: {str(e)}")

    # 第二步：sql查询数据
    try:
        query_result = execute_sql_query(sql_query)
    except Exception as e:
        # 处理执行SQL查询的错误
        raise Exception(f"Error in executing SQL query: {str(e)}")

    # 第三步：数据通过ai分析转成可运行代码
    try:
        runnable_code = ai_analyze_query_result_to_code_chain(input_text,query_result)
    except Exception as e:
        # 处理AI分析的错误
        raise Exception(f"Error in AI analysis: {str(e)}")

    # 第四步：运行代码获取svg数据
    try:
        svg_data = run_code_to_get_svg(runnable_code)
    except Exception as e:
        # 处理运行代码获取SVG的错误
        raise Exception(f"Error in generating SVG: {str(e)}")

    return svg_data





def execute_sql_query(sql_query: str, limit: int = 5) -> list:
    """
    根据提供的SQL查询执行查询并返回结果。

    参数:
    - sql_query: 要执行的SQL查询。

    返回:
    - 查询结果作为字典列表。
    """
    db = next(get_db())  # 获取数据库会话
    try:
        results = execute_sql(db, sql_query, limit)
        return results
    finally:
        db.close()
