visitor_register_schema = {
    "type": "object",
    "properties": {
        "visitor_information": {
            "type": "object",
            "properties": {
                "phone": {"type": ["string", "null"]},
                "name": {"type": ["string", "null"]},
                "id_number": {"type": ["string", "null"]},
                "license_plate": {"type": ["string", "null"]}
            },
            "required": ["phone", "name", "id_number", "license_plate"]
        },
        "visit_details": {
            "type": "object",
            "properties": {
                "visited_department": {"type": ["string", "null"]},
                "visited_person": {"type": ["string", "null"]},
                "visited_person_phone": {"type": ["string", "null"]},
                "appointment_time": {
                    "type": ["string", "null"],
                    "pattern": "^(\\d{4}-\\d{2}-\\d{2} (上午|下午)|EXAMPLE_APPOINTMENT_TIME|null)$"
                },
                "visit_unit": {"type": ["string", "null"]},
                "visit_reason": {"type": ["string", "null"]}
            },
            "required": ["visited_department", "visited_person", "visited_person_phone", "appointment_time", "visit_unit", "visit_reason"]
        }
    },
    "required": ["visitor_information", "visit_details"]
}
companion_register_schema = {
    "type": "object",
    "properties": {
        "companion_information": {
            "type": "object",
            "properties": {
                "name": {"type": ["string", "null"]},
                "phone": {"type": ["string", "null"]},
                "id_number": {"type": ["string", "null"]}
            },
            "required": ["name", "phone", "id_number"]
        }
    },
    "required": ["companion_information"]
}
