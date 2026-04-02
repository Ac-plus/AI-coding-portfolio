from datetime import datetime

from pydantic import BaseModel


class RoomResponse(BaseModel):
    id: str
    name: str
    capacity: int
    location: str


class OccupancyItemResponse(BaseModel):
    room_id: str
    room_name: str
    start_time: datetime
    end_time: datetime
    occupied: bool
    conflicting_booking_ids: list[str]
