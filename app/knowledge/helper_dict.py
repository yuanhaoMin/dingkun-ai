function_csv = [
    {
        "name": "query_csv",
        "description": "Provide data analysis services, especially when detecting .csv files or explicit data "
                       "analysis requests.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the data file.如果你不知道具体请询问用户。"
                },
                "query": {
                    "type": "string",
                    "description": "Query or request related to data analysis in chinese."
                }
            },
            "required": ["file_path", "query"]
        }
    }
]
function_navigation = [
    {
        "name": "navigate_to_page",
        "description": "Help users navigate to the desired page.",
        "parameters": {
            "type": "object",
            "properties": {
                "description": {
                    "type": "string",
                    "description": "User-described natural language requirements in chinese."
                }
            },
            "required": ["page_name"]
        }
    }
]
function_create_documentation = [
    {
        "name": "answer_documentation",
        "description": "Answer questions related to company's documentation, rules, and regulations.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Specific question about the document or rule."
                }
            },
            "required": ["document_name", "query"]
        }
    }
]