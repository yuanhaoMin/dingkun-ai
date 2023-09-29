front_end_functions = [
    {
        "name": "queryPreviousDatesAlarm",
        "description": "Retrieve the fence alarm trend for the past x days.(围栏告警趋势)",
        "parameters": {
            "type": "object",
            "properties": {
                "days": {
                    "type": "integer",
                    "description": "Number of days.",
                    "default": 7,
                }
            },
            "required": ["days"],
        },
    },
    {
        "name": "lastSeasonVisitorTendDatas",
        "description": "Retrieve the visitor trend data for the past x months.(访客数量趋势)",
        "parameters": {
            "type": "object",
            "properties": {
                "months": {
                    "type": "integer",
                    "description": "Number of months.",
                    "default": 3,
                }
            },
            "required": ["months"],
        },
    },
    {
        "name": "patrolTrend",
        "description": "Query the inspection trend for the recent x months.(巡检趋势)",
        "parameters": {
            "type": "object",
            "properties": {
                "months": {
                    "type": "integer",
                    "description": "Number of months.",
                    "default": 1,
                }
            },
            "required": ["months"],
        },
    },
    {
        "name": "queryInspectionCompletion",
        "description": "Query the inspection completion status. If 'region' is null, the function returns completion "
        "data for all regions. Otherwise, it returns data for the specified region. ("
        "查询巡检完成情况。)",
        "parameters": {
            "type": "object",
            "properties": {
                "region": {
                    "type": "string",
                    "description": "The specific region to query for inspection completion. If null, data for all "
                    "regions will be returned.",
                    "default": None,
                }
            },
            "required": [],
        },
    },
    {
        "name": "getInspectionProgress",
        "description": "Retrieve the inspection task completion status over a specified number of days, presented as a percentage. "
        "By default, it queries the progress for today.(巡检进度条)",
        "parameters": {
            "type": "object",
            "properties": {
                "days": {
                    "type": "integer",
                    "description": "The number of days over which to retrieve inspection task completion status. Default is 1, representing today's progress.",
                    "default": 1,
                }
            },
            "required": [],
        },
    },
]
