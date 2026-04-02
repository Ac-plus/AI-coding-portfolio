from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class BookingStatus(StrEnum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


@dataclass(slots=True)
class Booking:
    id: str
    room_id: str
    user_id: str
    start_time: datetime
    end_time: datetime
    status: BookingStatus
    created_at: datetime
    expires_at: datetime | None = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "room_id": self.room_id,
            "user_id": self.user_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }

    @classmethod
    def from_dict(cls, payload: dict) -> "Booking":
        expires_at = payload.get("expires_at")
        return cls(
            id=payload["id"],
            room_id=payload["room_id"],
            user_id=payload["user_id"],
            start_time=datetime.fromisoformat(payload["start_time"]),
            end_time=datetime.fromisoformat(payload["end_time"]),
            status=BookingStatus(payload["status"]),
            created_at=datetime.fromisoformat(payload["created_at"]),
            expires_at=datetime.fromisoformat(expires_at) if expires_at else None,
        )


@dataclass(slots=True)
class UserDailyBookingSummary:
    user_id: str
    date: str
    booking_count: int
