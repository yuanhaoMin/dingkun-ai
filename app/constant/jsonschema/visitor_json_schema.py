from jsonschema import validate, ValidationError


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
            "required": ["visited_department", "visited_person", "visited_person_phone", "appointment_time",
                         "visit_unit", "visit_reason"]
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
    "required": ["appointmentTime", "companyName", "contactOrg", "contactPerson", "idCard", "plateNumber", "remark",
                 "useName", "usePhone", "visitingReason"]
}

visitor_register_schema_smart_1 = {
    "type": "object",
    "properties": {
        "appointmentTime": {
            "type": ["string", "null"],
            "pattern": "^(\\d{4}-\\d{2}-\\d{2}|null)$"
        },
        "companyName": {"type": ["string", "null"]},
        "contactOrg": {"type": ["string", "null"]},
        "contactPerson": {"type": ["string", "null"]},
        "idCard": {"type": ["string", "null"]},
        "plateNumber": {"type": ["string", "null"]},
        "remark": {"type": ["string", "null"]},
        "useName": {"type": "string"},
        "usePhone": {"type": "string"},
        "visitingReason": {
            "type": "string",
            "enum": ["普通来访", "外来施工"]
        }
    },
    "required": ["useName", "usePhone"]
}

visitor_register_schema_smart_2 = {
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
                }
            }
        }
    }
}

data = [
    {
        "appointmentTime": "2023-09-01",
        "companyName": "ABC有限公司",
        "contactOrg": "销售部",
        "contactPerson": None,
        "idCard": "42010420000101234X",
        "plateNumber": "粤B12345",
        "remark": "商务洽谈",
        "useName": None,
        "usePhone": "1381399521",
        "visitingReason": "普通来访"
    },
    {
        "visitorChildDTOList": [
            {
                "useName": "李红",
                "usePhone": "13998765432",
                "idCard": None,
                "plateNumber": "粤B67890"
            },
            {
                "useName": "王青",
                "usePhone": "13765432109",
                "idCard": None,
                "plateNumber": None
            }
        ]
    }
]


def validate_jsons(json_list):
    errors = []

    for idx, json_obj in enumerate(json_list):
        try:
            if idx == 0:
                validate(instance=json_obj, schema=visitor_register_schema_smart_1)
            elif idx == 1:
                validate(instance=json_obj, schema=visitor_register_schema_smart_2)
        except ValidationError as e:
            path_to_error = ".".join(str(p) for p in e.path)
            errors.append(f"JSON {idx + 1} is not valid at key '{path_to_error}'. Reason: {e.message}")

    if errors:
        raise ValueError("\n".join(errors))

# try:
#     validate_jsons(data)
# except ValueError as e:
#     print(e)
