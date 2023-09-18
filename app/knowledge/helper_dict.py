functions = [
    {
        "name": "document_answer_service",
        "description": "Provide answers or services related to document files such as .txt, .pdf, and .docx.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the document file."
                },
                "question": {
                    "type": "string",
                    "description": "Question related to the document."
                }
            },
            "required": ["file_path", "question"]
        }
    },
    {
        "name": "redirect_page_service",
        "description": "Handle requests related to page redirection, system services, or any user interface interactions.",
        "parameters": {
            "type": "object",
            "properties": {
                "operation_text": {
                    "type": "string",
                    "description": "Text describing the operation or redirection request."
                }
            },
            "required": ["operation_text"]
        }
    },
    {
        "name": "data_analysis_service",
        "description": "Provide data analysis services, especially when detecting .csv files or explicit data analysis requests.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the data file."
                },
                "query": {
                    "type": "string",
                    "description": "Query or request related to data analysis."
                }
            },
            "required": ["file_path", "query"]
        }
    }
]
