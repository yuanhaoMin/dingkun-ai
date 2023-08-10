from typing import Tuple, List
from jsonschema import Draft7Validator


def validate_json(data: dict, schema: dict) -> Tuple[bool, List[str]]:
    validator = Draft7Validator(schema)
    errors = []
    for error in validator.iter_errors(data):
        errors.append(error.message)
    if errors:
        return False, errors
    return True, ["Validation passed."]

