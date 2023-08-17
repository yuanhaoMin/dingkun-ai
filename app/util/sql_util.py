from app.db.session.mysql_db import SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy.inspection import inspect
from sqlalchemy import text
from typing import Dict, List, Union, Type
import sqlparse


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def execute_sql(db: Session, sql: str, limit: int = 5):
    # # 添加LIMIT子句
    # if "LIMIT" not in sql.upper():
    #     sql += f" LIMIT {limit}"

    result = db.execute(text(sql))
    column_names = result.keys()
    # 将每行转换为字典
    return [dict(zip(column_names, row)) for row in result.fetchall()]


def validate_sql_against_model(
    sql: str, model: Type
) -> Dict[str, Union[bool, List[str]]]:
    """
    验证给定的 SQL 语句是否符合 SQLAlchemy 模型的结构。

    参数:
    - sql (str): 需要验证的 SQL 语句。
    - model (DeclarativeBase): SQLAlchemy 的数据模型。

    返回:
    - 字典，包括:
        - 'valid' (bool): 如果 SQL 与模型匹配则为 True，否则为 False。
        - 'errors' (List[str]): 不匹配的错误消息列表。
    """

    # 从给定的 SQL 中解析出列名
    parsed_statements = sqlparse.parse(sql)
    statement = parsed_statements[0]

    # 从 SQLAlchemy 模型中提取列名信息
    model_columns = [column.name for column in inspect(model).columns]

    # 初始化结果字典
    result = {"valid": True, "errors": []}

    # 比较解析的 SQL 列名与模型的列名
    referenced_columns = [
        str(token.get_real_name())
        for token in statement.tokens
        if isinstance(token, sqlparse.sql.Identifier)
    ]

    for column in referenced_columns:
        if column not in model_columns:
            error_message = f"SQL 中的列 {column} 在模型中未找到。"
            result["errors"].append(error_message)
            result["valid"] = False

    return result
