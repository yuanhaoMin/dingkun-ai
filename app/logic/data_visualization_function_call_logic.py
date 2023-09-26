import json
from fastapi import HTTPException


def build_url(endpoint, **params):
    """Builds a URL with given endpoint and query parameters."""
    base_url = "http://127.0.0.1:9000/mock/"
    if params:
        query_string = "&".join([f"{key}={value}" for key, value in params.items()])
        return f"{base_url}{endpoint}?{query_string}"
    return f"{base_url}{endpoint}"


# Endpoint functions
def query_previous_dates_alarm(days=7):
    return build_url("queryPreviousDatesAlarm", days=days)


def last_season_visitor_trend_data(months=3):
    return build_url("lastSeasonVisitorTendDatas", months=months)


def patrol_trend(months=1):
    return build_url("patrolTrend", months=months)


def query_inspection_completion():
    return build_url("queryInspectionCompletion")


def get_inspection_progress(days=1):
    return build_url("getInspectionProgress", days=days)


def determine_url_from_json(function_call):
    """Executes a function based on the provided JSON data."""
    # Dispatch dictionary
    function_map = {
        "queryPreviousDatesAlarm": query_previous_dates_alarm,
        "lastSeasonVisitorTendDatas": last_season_visitor_trend_data,
        "patrolTrend": patrol_trend,
        "queryInspectionCompletion": query_inspection_completion,
        "getInspectionProgress": get_inspection_progress,
    }
    try:
        function_name = function_call["name"]
        arguments = json.loads(function_call["arguments"])
        func = function_map.get(function_name)
        if func:
            return func(**arguments)
        else:
            raise ValueError(f"Function {function_name} not found")
    except KeyError as e:
        raise HTTPException(
            status_code=500, detail=f"Required key {e} not found in the input data"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing function {e}")
