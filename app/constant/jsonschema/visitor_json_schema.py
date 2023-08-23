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

companion_register_schema_old = {
    "type": "object",
    "properties": {
        "visitorChildDTOList": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "useName": {"type": ["string", "null"]},
                    "usePhone": {"type": ["string", "null"]},
                    "idCard": {"type": ["string", "null"]},
                    "plateNumber": {"type": ["string", "null"]}
                },
                "required": ["useName", "usePhone", "idCard", "plateNumber"]
            }
        }
    },
    "required": ["visitorChildDTOList"]
}

visitor_register_schema_old = {
    "type": "object",
    "properties": {
        "appointmentTime": {
            "type": ["string", "null"],
            "pattern": "^(\\d{4}-\\d{2}-\\d{2}|null)$"
        },
        "companyName": {
            "type": ["string", "null"]
        },
        "contactOrg": {
            "type": ["string", "null"]
        },
        "contactPerson": {
            "type": ["string", "null"]
        },
        "idCard": {
            "type": ["string", "null"]
        },
        "plateNumber": {
            "type": ["string", "null"]
        },
        "remark": {
            "type": ["string", "null"]
        },
        "useName": {
            "type": ["string", "null"]
        },
        "usePhone": {
            "type": ["string", "null"]
        },
        "visitingReason": {
            "type": ["string", "null"],
            "enum": ["普通来访", "外来施工", None]
        }
    },
    "required": ["appointmentTime", "companyName", "contactOrg", "contactPerson", "idCard", "plateNumber", "remark", "useName", "usePhone", "visitingReason"]
}

