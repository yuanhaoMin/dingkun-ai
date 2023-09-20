import os
from fastapi import HTTPException
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, MetaData, text
from app.api.dependency.database import table_schemas_instance

SQLALCHEMY_DATABASE_URL = os.environ.get("SQLALCHEMY_DATABASE_URL")

if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("SQLALCHEMY_DATABASE_URL not set in environment variables!")

engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
metadata = MetaData()


def get_all_table_names():
    with engine.connect() as connection:
        raw_table_names = connection.execute(text("SHOW TABLES")).fetchall()
    return [table[0] for table in raw_table_names]


def filter_log_tables(table_names):
    return [name for name in table_names if name.endswith("_log")]


def format_log_table_schemas(log_tables):
    table_strings = []
    for table_name, table in log_tables.items():
        columns_str_list = [
            f"{column.name}: {column.type.compile(engine.dialect)}"
            for column in table.columns
        ]
        table_string = f"Table: {table_name}\n" + "\n".join(columns_str_list)
        table_strings.append(table_string)
    return "\n\n".join(table_strings)


def reflect_log_tables():
    try:
        metadata.clear()
        all_table_names = get_all_table_names()
        log_table_names = filter_log_tables(all_table_names)
        metadata.reflect(engine, only=log_table_names)
        log_tables = metadata.tables
        formatted_schemas = format_log_table_schemas(log_tables)
        table_schemas_instance.set_schemas(formatted_schemas)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error while reflecting log tables: {e}")