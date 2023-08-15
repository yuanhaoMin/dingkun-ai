from app.util.openai_util import completion
from app.util.text_util import create_prompt_from_template_file


def natural_language_to_sql_chain(text: str, table_schema: str, current_date: str, day_of_week: str) -> str:
    """
    自然语言转换为SQL查询的方法。

    参数:
    - text: 用户提供的自然语言输入。
    - table_schema: SQLAlchemy模型描述的表结构。
    - current_date: 当前日期。
    - day_of_week: 当前星期。

    返回:
    - 生成的SQL查询。
    """

    # 使用提示词模板并替换其中的内容
    replacements = {
        "table_schema": """
    class UwbPatrolLog(Base):
        __tablename__ = 'uwb_patrol_log'
        id = Column(Integer, primary_key=True, autoincrement=True)
        unit_id = Column(Integer)
        patrol_code = Column(String(255))
        patrol_name = Column(String(255))
        person_code = Column(Integer)
        area_code = Column(Integer)
        into_time = Column(DateTime)
        out_time = Column(DateTime)
        create_time = Column(DateTime)
        update_time = Column(DateTime)
        """,
        "current_date": current_date,
        "day_of_week": day_of_week
    }

    prompt = create_prompt_from_template_file(filename="sql_generator_prompts", replacements=replacements)

    # 构造与AI对话的消息列表
    messages = [{"role": "system", "content": prompt}]

    sql_query = completion(messages)

    return sql_query
