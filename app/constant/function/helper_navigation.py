name_time_page_listRows_extract = [
    {
        "name": "extracting",
        "description": "extracting",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "person name"
                },
                "start_time": {
                    "type": "string",
                    "description": "Start time in the format '2023-09-20 11:00'."
                },
                "end_time": {
                    "type": "string",
                    "description": "End time in the format '2023-09-20 12:00'. '"
                },
                "page": {
                    "type": "integer",
                    "description": "The page number for pagination. If not returned, the value should be assumed as the default or the first page."
                },
                "listRows": {
                    "type": "integer",
                    "description": "The number of rows per page for pagination. If not returned, a default value or system setting should be used."
                }
            },
            "required": ["name", "start_time", "end_time"]
        }
    }
]
name_start_time_end_time_extract = [
    {
        "name": "extracting",
        "description": "extracting",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "person name"
                },
                "start_time": {
                    "type": "string",
                    "description": "Start time in the format '2023-09-20 11:00'."
                },
                "end_time": {
                    "type": "string",
                    "description": "End time in the format '2023-09-20 12:00'. '"
                }
            },
            "required": ["name", "start_time", "end_time"]
        }
    }
]

name_extract = [
    {
        "name": "extracting",
        "description": "extracting",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                }
            },
            "required": ["file_path", "query"]
        }
    }
]

