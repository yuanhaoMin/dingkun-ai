information_extraction_schema = [
    {
        "name": "information_extraction",
        "description": "Extract information from a given context, especially useful for chart operations.",
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "The main operation type such as 'move', 'swap', 'display', 'replace', or 'reset'.",
                    "enum": ["move", "display", "replace", "reset"]
                },
                "target": {
                    "type": "string",
                    "description": "The target chart's name that the operation acts upon. If not returned, the value should be an empty string.",
                },
                "position": {
                    "type": "string",
                    "description": "Position number to move the target chart to. If not returned, the value should be an empty string.",
                },
                "newTarget": {
                    "type": "string",
                    "description": "New chart's name to replace the target with. If not returned, the value should be an empty string.",
                }
            },
            "required": ["action", "target"]
        }
    }
]
table_data_time_and_pagination_schema = [
    {
        "name": "get_table_data_time_and_pagination",
        "description": "Retrieve the start time, end time, and pagination details for the table data required by the user, with precision up to hours, minutes, and seconds.",
        "parameters": {
            "type": "object",
            "properties": {
                "start_time": {
                    "type": "string",
                    "description": "The starting time of the data the user requires. It should be in the format 'YYYY-MM-DD HH:mm:ss'. If not returned, the value should be an empty string.",
                    "pattern": "^[0-9]{4}-[0-1][0-9]-[0-3][0-9] [0-2][0-9]:[0-5][0-9]:[0-5][0-9]$"
                },
                "end_time": {
                    "type": "string",
                    "description": "The ending time of the data the user requires. It should be in the format 'YYYY-MM-DD HH:mm:ss'. If not returned, the value should be an empty string.",
                    "pattern": "^[0-9]{4}-[0-1][0-9]-[0-3][0-9] [0-2][0-9]:[0-5][0-9]:[0-5][0-9]$"
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
            "required": ["start_time", "end_time"]
        }
    }
]

