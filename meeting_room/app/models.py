from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Room:
    id: str
    name: str
    capacity: int

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Booking:
    id: str
    room_id: str
    user_id: str
    title: str
    start_time: str
    end_time: str
    status: str
    created_at: str

    def to_dict(self) -> dict:
        return asdict(self)
