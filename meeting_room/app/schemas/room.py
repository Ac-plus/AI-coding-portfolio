from pydantic import BaseModel


class RoomResponse(BaseModel):
    id: str
    name: str
    capacity: int
    location: str
