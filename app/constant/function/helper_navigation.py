from app.util.time_utll import get_current_day_times

start_time, end_time = get_current_day_times()

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
                    "description": f"Start time in the format '{start_time}'."
                },
                "end_time": {
                    "type": "string",
                    "description": f"End time in the format '{end_time}'."
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
                    "description": f"Start time in the format '{start_time}'."
                },
                "end_time": {
                    "type": "string",
                    "description": f"End time in the format '{end_time}'."
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

