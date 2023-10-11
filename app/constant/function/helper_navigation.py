from app.util.time_util import get_current_day_times


def get_name_time_page_listRows_extract():
    start_time, end_time = get_current_day_times()
    return [
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
                        "description": f"Start time in the format '{start_time}'.",
                        "default": start_time
                    },
                    "end_time": {
                        "type": "string",
                        "description": f"End time in the format '{end_time}'.",
                        "default": end_time
                    },
                    "page": {
                        "type": "integer",
                        "description": "The page number for pagination. If not returned, the value should be assumed as the default or the first page.",
                        "default": 1
                    },
                    "listRows": {
                        "type": "integer",
                        "description": "The number of rows per page for pagination. If not returned, a default value or system setting should be used.",
                        "default": 20
                    }
                },
                "required": ["name", "start_time", "end_time"]
            }
        }
    ]


def get_name_start_time_end_time_extract():
    start_time, end_time = get_current_day_times()
    return [
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
                        "description": f"Start time in the format '{start_time}'.",
                        "default": start_time
                    },
                    "end_time": {
                        "type": "string",
                        "description": f"End time in the format '{end_time}'.",
                        "default": end_time
                    }
                },
                "required": ["name", "start_time", "end_time"]
            }
        }
    ]


def get_name_extract():
    return [
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
                "required": ["name"]
            }
        }
    ]
