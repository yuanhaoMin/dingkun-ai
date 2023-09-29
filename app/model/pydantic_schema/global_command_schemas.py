from enum import Enum
from pydantic import BaseModel


class Route(str, Enum):
    Track = "Track"
    Screen = "Screen"
    Help = "Help"
    OneClickSearch = "OneClickSearch"


class VoiceRedirectRequest(BaseModel):
    user_id: int
    user_message: str
    route: Route
