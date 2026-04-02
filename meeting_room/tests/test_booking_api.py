from datetime import timedelta

import pytest
from fastapi import HTTPException

from app.api.routes_bookings import cancel_booking, create_booking, list_bookings
from app.api.routes_maintenance import release_expired_bookings
from app.api.routes_rooms import list_rooms
from app.schemas.booking import BookingCreateRequest
from app.services import ExpirationService


def test_list_rooms_returns_seeded_rooms(booking_service, room_service):
    response = list_rooms(room_service=room_service)

    assert response[0].id == "room-a"


def test_create_and_cancel_booking_via_route(booking_service, base_now):
    payload = BookingCreateRequest(
        room_id="room-a",
        user_id="user-1",
        start_time=base_now + timedelta(hours=1),
        end_time=base_now + timedelta(hours=2),
    )

    created = create_booking(payload, booking_service=booking_service)
    cancelled = cancel_booking(created.id, user_id="user-1", booking_service=booking_service)

    assert created.room_id == "room-a"
    assert cancelled.status == "cancelled"


def test_route_returns_conflict_for_overlapping_booking(booking_service, base_now):
    first = BookingCreateRequest(
        room_id="room-a",
        user_id="user-1",
        start_time=base_now + timedelta(hours=1),
        end_time=base_now + timedelta(hours=2),
    )
    second = BookingCreateRequest(
        room_id="room-a",
        user_id="user-2",
        start_time=base_now + timedelta(hours=1, minutes=30),
        end_time=base_now + timedelta(hours=2, minutes=30),
    )

    create_booking(first, booking_service=booking_service)

    with pytest.raises(HTTPException) as error:
        create_booking(second, booking_service=booking_service)

    assert error.value.status_code == 409


def test_route_lists_filtered_bookings(booking_service, base_now):
    create_booking(
        BookingCreateRequest(
            room_id="room-a",
            user_id="user-1",
            start_time=base_now + timedelta(hours=1),
            end_time=base_now + timedelta(hours=2),
        ),
        booking_service=booking_service,
    )
    create_booking(
        BookingCreateRequest(
            room_id="room-a",
            user_id="user-2",
            start_time=base_now + timedelta(hours=3),
            end_time=base_now + timedelta(hours=4),
        ),
        booking_service=booking_service,
    )

    response = list_bookings(user_id="user-2", room_id=None, date=None, include_inactive=True, booking_service=booking_service)

    assert len(response) == 1
    assert response[0].user_id == "user-2"


def test_release_expired_endpoint_reports_released_booking(tmp_path, base_now):
    booking_service, _, expiration_service = _build_services(tmp_path)
    created = booking_service.create_booking(
        room_id="room-a",
        user_id="user-1",
        start_time=base_now + timedelta(hours=1),
        end_time=base_now + timedelta(hours=2),
        now=base_now - timedelta(minutes=31),
    )

    response = release_expired_bookings(expiration_service=expiration_service)

    assert response.released_count == 1
    assert created.id in response.released_booking_ids


def test_release_expired_endpoint_returns_empty_when_nothing_expired(tmp_path):
    _, _, expiration_service = _build_services(tmp_path)

    response = release_expired_bookings(expiration_service=expiration_service)

    assert response.released_count == 0
    assert response.released_booking_ids == []


def _build_services(tmp_path):
    from app.concurrency.lock_manager import LockManager
    from app.models.room import Room
    from app.repositories.booking_repository import BookingRepository
    from app.repositories.room_repository import RoomRepository
    from app.services import BookingService, RoomService

    room_repository = RoomRepository(tmp_path / "rooms.json")
    booking_repository = BookingRepository(tmp_path / "bookings.json")
    lock_manager = LockManager()
    room_repository.save_rooms([Room(id="room-a", name="A01", capacity=12, location="3F")])

    room_service = RoomService(room_repository)
    booking_service = BookingService(booking_repository, room_repository, lock_manager)
    expiration_service = ExpirationService(booking_repository, lock_manager)
    return booking_service, room_service, expiration_service
