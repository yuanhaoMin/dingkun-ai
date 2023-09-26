functions = [
    {
        "text": "查看事故发生前一刻的人员分布图",
        "action": "activate",
        "target": "emergency",
        "attribute": "distribution_before_accident",
        "route": "Trajectory_Management_Emergency_Response",
    },
    {
        "text": "查询人员的历史轨迹",
        "action": "display",
        "target": "person",
        "attribute": "historical_trajectory",
        "route": "Trajectory_Management_Historical",
        "name": None,
        "time_start": None,
        "time_end": None,
    },
    {
        "text": "查询人员的最终位置",
        "action": "view",
        "target": "person",
        "attribute": "final_position",
        "route": "Track",
        "name": None,
    },
    {
        "text": "只想要显示人员轨迹信息",
        "action": "display",
        "target": "map",
        "attribute": "person_trajectory",
        "route": "Track",
    },
    {
        "text": "我想看看某个人员的详细信息",
        "action": "view",
        "target": "person",
        "attribute": "details",
        "route": "Track",
        "name": None,
    },
    {
        "text": "查看特定人员实时轨迹",
        "action": "view",
        "target": "person",
        "attribute": "real_time",
        "route": "Track",
        "name": None,
    },
    {
        "text": "查看在线人员列表",
        "action": "view",
        "target": "person",
        "attribute": "online_list",
        "route": "Track",
    },
    {
        "text": "查看离线人员列表",
        "action": "view",
        "target": "person",
        "attribute": "offline_list",
        "route": "Track",
    },
    {
        "text": "查看在线车辆列表",
        "action": "view",
        "target": "vehicle",
        "attribute": "online_list",
        "route": "Track",
    },
]


name_time_start_time_end_extract = [
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
                "time_start": {
                    "type": "string",
                    "description": "Start time in the format '2023-09-20 11:00'."
                },
                "time_end": {
                    "type": "string",
                    "description": "End time in the format '2023-09-20 12:00'. '"
                }
            },
            "required": ["name", "time_start", "time_end"]
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
