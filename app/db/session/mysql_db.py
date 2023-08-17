from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, MetaData, text

from app.api.dependency.database import table_schemas_instance

SQLALCHEMY_DATABASE_URL = "mysql+mysqldb://root:root@localhost/uwb_test"

engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

metadata = MetaData()


# # 存储以_log结尾的表结构
# log_tables = {}


def reflect_log_tables():
    # 清空元数据中的现有表
    metadata.clear()

    # 使用数据库连接获取所有表名
    with engine.connect() as connection:
        raw_table_names = connection.execute(text("SHOW TABLES")).fetchall()
        table_names = [table[0] for table in raw_table_names]

    # 过滤出以 `_log` 结尾的表名
    log_table_names = [name for name in table_names if name.endswith("_log")]

    # 只反射以 `_log` 结尾的表
    metadata.reflect(engine, only=log_table_names)

    log_tables = metadata.tables

    table_strings = []
    for table_name, table in log_tables.items():
        columns_str_list = [
            f"{column.name}: {column.type.compile(engine.dialect)}"
            for column in table.columns
        ]
        table_string = f"Table: {table_name}\n" + "\n".join(columns_str_list)
        table_strings.append(table_string)

    table_schemas_instance.set_schemas("\n\n".join(table_strings))
