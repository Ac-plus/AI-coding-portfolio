from datetime import datetime

from pydantic import BaseModel, Field


class BookingCreateRequest(BaseModel):
    room_id: str = Field(min_length=1)
    user_id: str = Field(min_length=1)
    start_time: datetime
    end_time: datetime


class BookingResponse(BaseModel):
    id: str
    room_id: str
    user_id: str
    start_time: datetime
    end_time: datetime
    status: str
    created_at: datetime
    expires_at: datetime | None = None


class BookingListItemResponse(BookingResponse):
    pass


class ReleaseExpiredResponse(BaseModel):
    released_count: int
    released_booking_ids: list[str]
