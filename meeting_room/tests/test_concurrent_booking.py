from datetime import timedelta
from pathlib import Path
import threading
from uuid import uuid4

import pytest

from app.concurrency import LockManager, has_time_conflict
from app.models.booking import Booking, BookingStatus
from app.models.room import Room
from app.models.user import User
from app.repositories.booking_repository import BookingRepository
from app.repositories.room_repository import RoomRepository
from app.repositories.user_repository import UserRepository
from app.services.booking_service import BookingService


def _make_candidate(user_id, base_now):
    return Booking(
        id=str(uuid4()),
        room_id="room-a",
        user_id=user_id,
        start_time=base_now + timedelta(hours=2),
        end_time=base_now + timedelta(hours=3),
        status=BookingStatus.ACTIVE,
        created_at=base_now,
        expires_at=base_now + timedelta(minutes=30),
    )


def test_concurrent_booking_allows_only_one_winner(tmp_path: Path, base_now):
    repo = BookingRepository(tmp_path / "bookings.json")
    repo.save_bookings([])
    lock_manager = LockManager()

    results: list[str] = []
    results_lock = threading.Lock()
    start_barrier = threading.Barrier(6)

    def attempt_booking(user_id: str) -> None:
        candidate = _make_candidate(user_id, base_now)
        start_barrier.wait()
        with lock_manager.acquire_booking_flow(candidate.room_id, timeout=1):
            latest = repo.list_bookings(include_inactive=False)
            if has_time_conflict(candidate, latest):
                outcome = "conflict"
            else:
                latest.append(candidate)
                repo.save_bookings(latest)
                outcome = "booked"
        with results_lock:
            results.append(outcome)

    threads = [
        threading.Thread(target=attempt_booking, args=(f"user-{index}",))
        for index in range(5)
    ]

    for thread in threads:
        thread.start()

    start_barrier.wait()

    for thread in threads:
        thread.join(timeout=2)
        assert not thread.is_alive()

    persisted = repo.list_bookings(include_inactive=False)

    assert results.count("booked") == 1
    assert results.count("conflict") == 4
    assert len(persisted) == 1


def test_acquire_resources_uses_sorted_order_for_shared_inputs():
    lock_manager = LockManager()

    with lock_manager.acquire_resources(["room:2", "room:1", "room:2"], timeout=1):
        with lock_manager.acquire_resources(["room:1", "room:2"], timeout=1):
            assert True


def test_concurrent_booking_allows_different_rooms(tmp_path: Path, base_now):
    repo = BookingRepository(tmp_path / "bookings.json")
    repo.save_bookings([])
    lock_manager = LockManager()
    results: list[str] = []
    results_lock = threading.Lock()
    start_barrier = threading.Barrier(3)

    def attempt_booking(room_id: str, user_id: str) -> None:
        candidate = Booking(
            id=str(uuid4()),
            room_id=room_id,
            user_id=user_id,
            start_time=base_now + timedelta(hours=2),
            end_time=base_now + timedelta(hours=3),
            status=BookingStatus.ACTIVE,
            created_at=base_now,
            expires_at=base_now + timedelta(minutes=30),
        )
        start_barrier.wait()
        with lock_manager.acquire_booking_flow(candidate.room_id, timeout=1):
            latest = repo.list_bookings(include_inactive=False)
            if has_time_conflict(candidate, latest):
                outcome = "conflict"
            else:
                latest.append(candidate)
                repo.save_bookings(latest)
                outcome = "booked"
        with results_lock:
            results.append(outcome)

    threads = [
        threading.Thread(target=attempt_booking, args=("room-a", "user-1")),
        threading.Thread(target=attempt_booking, args=("room-b", "user-2")),
    ]

    for thread in threads:
        thread.start()

    start_barrier.wait()

    for thread in threads:
        thread.join(timeout=2)
        assert not thread.is_alive()

    assert results.count("booked") == 2


def test_concurrent_booking_allows_same_room_different_time_slots(tmp_path: Path, base_now):
    repo = BookingRepository(tmp_path / "bookings.json")
    repo.save_bookings([])
    lock_manager = LockManager()
    results: list[str] = []
    results_lock = threading.Lock()
    start_barrier = threading.Barrier(3)

    def attempt_booking(user_id: str, offset_hours: int) -> None:
        candidate = Booking(
            id=str(uuid4()),
            room_id="room-a",
            user_id=user_id,
            start_time=base_now + timedelta(hours=offset_hours),
            end_time=base_now + timedelta(hours=offset_hours + 1),
            status=BookingStatus.ACTIVE,
            created_at=base_now,
            expires_at=base_now + timedelta(minutes=30),
        )
        start_barrier.wait()
        with lock_manager.acquire_booking_flow(candidate.room_id, timeout=1):
            latest = repo.list_bookings(include_inactive=False)
            if has_time_conflict(candidate, latest):
                outcome = "conflict"
            else:
                latest.append(candidate)
                repo.save_bookings(latest)
                outcome = "booked"
        with results_lock:
            results.append(outcome)

    threads = [
        threading.Thread(target=attempt_booking, args=("user-1", 2)),
        threading.Thread(target=attempt_booking, args=("user-2", 4)),
    ]

    for thread in threads:
        thread.start()

    start_barrier.wait()

    for thread in threads:
        thread.join(timeout=2)
        assert not thread.is_alive()

    assert results.count("booked") == 2


def test_lock_manager_times_out_when_resource_is_held():
    lock_manager = LockManager()
    ready = threading.Event()
    release = threading.Event()

    def hold_lock() -> None:
        with lock_manager.acquire_resources(["room:1"], timeout=1):
            ready.set()
            release.wait(timeout=1)

    holder = threading.Thread(target=hold_lock)
    holder.start()
    ready.wait(timeout=1)

    with pytest.raises(TimeoutError):
        with lock_manager.acquire_resources(["room:1"], timeout=0.01):
            assert False

    release.set()
    holder.join(timeout=2)
    assert not holder.is_alive()


def test_concurrent_create_and_cancel_keeps_consistent_state(tmp_path: Path, base_now):
    room_repository = RoomRepository(tmp_path / "rooms.json")
    booking_repository = BookingRepository(tmp_path / "bookings.json")
    user_repository = UserRepository(tmp_path / "users.json")
    lock_manager = LockManager()
    room_repository.save_rooms([Room(id="room-a", name="A01", capacity=12, location="3F")])
    user_repository.save_users(
        [
            User(id="user-1", name="Alice", team="Platform"),
            User(id="user-2", name="Bob", team="Operations"),
        ]
    )
    booking_service = BookingService(
        booking_repository,
        room_repository,
        lock_manager,
        user_repository=user_repository,
    )
    original = booking_service.create_booking(
        room_id="room-a",
        user_id="user-1",
        start_time=base_now + timedelta(hours=2),
        end_time=base_now + timedelta(hours=3),
        now=base_now,
    )

    outcomes: list[str] = []
    outcome_lock = threading.Lock()
    barrier = threading.Barrier(3)

    def cancel_original() -> None:
        barrier.wait()
        booking_service.cancel_booking(original.id, user_id="user-1")
        with outcome_lock:
            outcomes.append("cancelled-original")

    def create_replacement() -> None:
        barrier.wait()
        try:
            booking_service.create_booking(
                room_id="room-a",
                user_id="user-2",
                start_time=base_now + timedelta(hours=2),
                end_time=base_now + timedelta(hours=3),
                now=base_now,
            )
            result = "created-replacement"
        except Exception:
            result = "replacement-failed"
        with outcome_lock:
            outcomes.append(result)

    threads = [
        threading.Thread(target=cancel_original),
        threading.Thread(target=create_replacement),
    ]
    for thread in threads:
        thread.start()

    barrier.wait()

    for thread in threads:
        thread.join(timeout=2)
        assert not thread.is_alive()

    bookings = booking_service.list_bookings(include_inactive=True)
    active = [booking for booking in bookings if booking.status == BookingStatus.ACTIVE]
    persisted = booking_repository.list_bookings(include_inactive=True)

    assert len(active) <= 1
    assert len(persisted) == len(bookings)
    assert sorted(outcomes) in [
        ["cancelled-original", "created-replacement"],
        ["cancelled-original", "replacement-failed"],
    ]
