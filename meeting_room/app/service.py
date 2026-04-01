from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict
from datetime import datetime, timedelta
from threading import RLock
from uuid import uuid4

from .models import Booking, Room


class BookingError(Exception):
    """Business validation error for booking flows."""


class BookingService:
    MAX_BOOKING_HOURS = 4
    MAX_DAILY_BOOKINGS = 3
    MIN_ADVANCE_MINUTES = 15
    AUTO_RELEASE_AFTER_MINUTES = 30

    def __init__(self) -> None:
        self._lock = RLock()
        self._rooms = [
            Room(id="room-a", name="A101", capacity=6),
            Room(id="room-b", name="B201", capacity=10),
            Room(id="room-c", name="C301", capacity=20),
        ]
        self._room_map = {room.id: room for room in self._rooms}
        self._bookings: dict[str, Booking] = {}
        self._bookings_by_room: dict[str, list[str]] = defaultdict(list)

    def list_rooms(self) -> list[dict]:
        return [room.to_dict() for room in self._rooms]

    def list_bookings(self) -> list[dict]:
        with self._lock:
            self._cleanup_expired_locked()
            bookings = sorted(
                self._bookings.values(),
                key=lambda booking: (booking.start_time, booking.created_at),
            )
            return [booking.to_dict() for booking in bookings]

    def create_booking(self, payload: dict) -> dict:
        with self._lock:
            self._cleanup_expired_locked()

            room_id = str(payload.get("room_id", "")).strip()
            user_id = str(payload.get("user_id", "")).strip()
            title = str(payload.get("title", "")).strip()
            start_time_raw = str(payload.get("start_time", "")).strip()
            end_time_raw = str(payload.get("end_time", "")).strip()

            if not room_id or room_id not in self._room_map:
                raise BookingError("会议室不存在。")
            if not user_id:
                raise BookingError("user_id 不能为空。")
            if not title:
                raise BookingError("title 不能为空。")

            start_dt = self._parse_time(start_time_raw, "start_time")
            end_dt = self._parse_time(end_time_raw, "end_time")
            self._validate_time_window(start_dt, end_dt)
            self._validate_daily_limit(user_id, start_dt.date())
            self._validate_no_conflict(room_id, start_dt, end_dt)

            now = datetime.now().replace(microsecond=0)
            booking = Booking(
                id=str(uuid4()),
                room_id=room_id,
                user_id=user_id,
                title=title,
                start_time=start_dt.isoformat(timespec="minutes"),
                end_time=end_dt.isoformat(timespec="minutes"),
                status="active",
                created_at=now.isoformat(timespec="seconds"),
            )
            self._bookings[booking.id] = booking
            self._bookings_by_room[room_id].append(booking.id)
            return booking.to_dict()

    def cancel_booking(self, booking_id: str) -> dict:
        with self._lock:
            self._cleanup_expired_locked()
            booking = self._bookings.get(booking_id)
            if booking is None:
                raise BookingError("预订不存在。")
            if booking.status == "cancelled":
                raise BookingError("预订已取消。")

            booking.status = "cancelled"
            return booking.to_dict()

    def _parse_time(self, value: str, field_name: str) -> datetime:
        try:
            parsed = datetime.fromisoformat(value)
        except ValueError as exc:
            raise BookingError(f"{field_name} 时间格式错误。") from exc
        return parsed.replace(second=0, microsecond=0)

    def _validate_time_window(self, start_dt: datetime, end_dt: datetime) -> None:
        now = datetime.now().replace(second=0, microsecond=0)

        if end_dt <= start_dt:
            raise BookingError("结束时间必须晚于开始时间。")
        if start_dt < now:
            raise BookingError("不能预订过去时间。")
        if start_dt < now + timedelta(minutes=self.MIN_ADVANCE_MINUTES):
            raise BookingError("必须至少提前15分钟预订。")
        if end_dt - start_dt > timedelta(hours=self.MAX_BOOKING_HOURS):
            raise BookingError("单次预订不能超过4小时。")

    def _validate_daily_limit(self, user_id: str, booking_date) -> None:
        count = 0
        for booking in self._bookings.values():
            if booking.status != "active":
                continue
            if booking.user_id != user_id:
                continue
            if datetime.fromisoformat(booking.start_time).date() == booking_date:
                count += 1
        if count >= self.MAX_DAILY_BOOKINGS:
            raise BookingError("同一用户每天最多预订3个时段。")

    def _validate_no_conflict(
        self,
        room_id: str,
        start_dt: datetime,
        end_dt: datetime,
    ) -> None:
        for booking_id in self._bookings_by_room[room_id]:
            booking = self._bookings[booking_id]
            if booking.status != "active":
                continue

            existing_start = datetime.fromisoformat(booking.start_time)
            existing_end = datetime.fromisoformat(booking.end_time)
            if start_dt < existing_end and end_dt > existing_start:
                raise BookingError("该会议室在所选时间段已被预订。")

    def _cleanup_expired_locked(self) -> None:
        now = datetime.now().replace(second=0, microsecond=0)
        auto_release_at = now - timedelta(minutes=self.AUTO_RELEASE_AFTER_MINUTES)
        for booking in self._bookings.values():
            if booking.status != "active":
                continue
            start_dt = datetime.fromisoformat(booking.start_time)
            if start_dt <= auto_release_at:
                booking.status = "cancelled"


def booking_to_dict(booking: Booking) -> dict:
    return asdict(booking)
