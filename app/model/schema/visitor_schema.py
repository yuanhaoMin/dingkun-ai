from pydantic import BaseModel
from typing import List, Optional


# {
#   "sessionId": "abc123",
#   "text": "Some text here",
#   "departments": [
#     {"id": 1, "name": "HR"},
#     {"id": 2, "name": "Engineering"}
#   ]
# }

class Department(BaseModel):
    id: int
    name: str


class DetermineFunctionCallRequest(BaseModel):
    sessionId: str
    text: str
    departments: Optional[List[Department]] = None
