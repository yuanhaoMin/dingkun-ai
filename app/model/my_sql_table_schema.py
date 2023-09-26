class TableSchemas:
    def __init__(self):
        self.schemas = ""

    def set_schemas(self, schemas):
        self.schemas = schemas

    def get_schemas(self):
        return self.schemas


table_schemas_instance = TableSchemas()


def get_table_schemas():
    return table_schemas_instance
