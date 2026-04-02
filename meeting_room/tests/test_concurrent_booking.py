from datetime import timedelta
from pathlib import Path
import threading
from uuid import uuid4

from app.concurrency import LockManager, has_time_conflict
from app.models.booking import Booking, BookingStatus
from app.repositories.booking_repository import BookingRepository


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
        thread.join()

    persisted = repo.list_bookings(include_inactive=False)

    assert results.count("booked") == 1
    assert results.count("conflict") == 4
    assert len(persisted) == 1


def test_acquire_resources_uses_sorted_order_for_shared_inputs():
    lock_manager = LockManager()

    with lock_manager.acquire_resources(["room:2", "room:1", "room:2"], timeout=1):
        with lock_manager.acquire_resources(["room:1", "room:2"], timeout=1):
            assert True
