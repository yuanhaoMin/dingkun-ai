functions = [
    {
        "name": "queryPreviousDatesAlarm",
        "description": "Retrieve the fence alarm trend for the past x days.",
        "parameters": {
            "type": "object",
            "properties": {
                "days": {
                    "type": "integer",
                    "description": "Number of days.",
                    "default": 7
                }
            },
            "required": ["days"]
        }
    },
    {
        "name": "lastSeasonVisitorTendDatas",
        "description": "Retrieve the visitor trend data for the past x months.",
        "parameters": {
            "type": "object",
            "properties": {
                "months": {
                    "type": "integer",
                    "description": "Number of months.",
                    "default": 3
                }
            },
            "required": ["months"]
        }
    },
    {
        "name": "patrolTrend",
        "description": "Query the inspection trend for the current month.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    }
]