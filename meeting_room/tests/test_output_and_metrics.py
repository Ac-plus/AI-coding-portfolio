import logging
from io import StringIO
from datetime import timedelta

from app.models.room import Room
from app.models.user import User
from app.repositories.booking_repository import BookingRepository
from app.repositories.room_repository import RoomRepository
from app.repositories.user_repository import UserRepository
from app.services import BookingConflictError, BookingService, ExpirationService, MetricsService
from app.concurrency.lock_manager import LockManager


def build_services(tmp_path):
    room_repository = RoomRepository(tmp_path / "rooms.json")
    booking_repository = BookingRepository(tmp_path / "bookings.json")
    user_repository = UserRepository(tmp_path / "users.json")
    metrics_service = MetricsService()
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
        metrics_service=metrics_service,
    )
    expiration_service = ExpirationService(
        booking_repository,
        lock_manager,
        metrics_service=metrics_service,
    )
    return booking_service, expiration_service, metrics_service


def test_logs_capture_booking_conflict_cancel_and_auto_release(tmp_path, base_now, caplog):
    booking_service, expiration_service, _ = build_services(tmp_path)
    caplog.set_level(logging.INFO)

    created = booking_service.create_booking(
        room_id="room-a",
        user_id="user-1",
        start_time=base_now + timedelta(hours=1),
        end_time=base_now + timedelta(hours=2),
        now=base_now,
    )

    try:
        booking_service.create_booking(
            room_id="room-a",
            user_id="user-2",
            start_time=base_now + timedelta(hours=1, minutes=30),
            end_time=base_now + timedelta(hours=2, minutes=30),
            now=base_now,
        )
    except BookingConflictError:
        pass

    booking_service.cancel_booking(created.id, user_id="user-1")

    another = booking_service.create_booking(
        room_id="room-a",
        user_id="user-1",
        start_time=base_now + timedelta(hours=3),
        end_time=base_now + timedelta(hours=4),
        now=base_now - timedelta(minutes=31),
    )
    expiration_service.release_expired_bookings(now=base_now)

    log_text = "\n".join(record.getMessage() for record in caplog.records)

    assert "booking_created" in log_text
    assert "booking_conflict" in log_text
    assert "booking_cancelled" in log_text
    assert "auto_release" in log_text
    assert another.id in log_text


def test_formatted_logs_include_timestamp_room_user_and_reason(tmp_path, base_now):
    booking_service, _, _ = build_services(tmp_path)
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
    logger = logging.getLogger("meeting_room.booking")
    original_handlers = list(logger.handlers)
    original_level = logger.level
    logger.handlers = [handler]
    logger.setLevel(logging.INFO)
    logger.propagate = False

    try:
        try:
            booking_service.create_booking(
                room_id="room-a",
                user_id="user-2",
                start_time=base_now - timedelta(minutes=5),
                end_time=base_now + timedelta(minutes=30),
                now=base_now,
            )
        except Exception:
            pass
    finally:
        handler.flush()
        logger.handlers = original_handlers
        logger.setLevel(original_level)
        logger.propagate = True

    output = stream.getvalue()
    assert "booking_rejected" in output
    assert "room_id=room-a" in output
    assert "user_id=user-2" in output
    assert "reason=rule_validation" in output
    assert output[:4].isdigit()


def test_metrics_snapshot_contains_required_outcomes(tmp_path, base_now):
    booking_service, expiration_service, metrics_service = build_services(tmp_path)
    created = booking_service.create_booking(
        room_id="room-a",
        user_id="user-1",
        start_time=base_now + timedelta(hours=1),
        end_time=base_now + timedelta(hours=2),
        now=base_now,
    )

    try:
        booking_service.create_booking(
            room_id="room-a",
            user_id="user-2",
            start_time=base_now + timedelta(hours=1, minutes=15),
            end_time=base_now + timedelta(hours=2, minutes=15),
            now=base_now,
        )
    except BookingConflictError:
        pass

    booking_service.cancel_booking(created.id, user_id="user-1")
    booking_service.create_booking(
        room_id="room-a",
        user_id="user-1",
        start_time=base_now + timedelta(hours=3),
        end_time=base_now + timedelta(hours=4),
        now=base_now - timedelta(minutes=31),
    )
    expiration_service.release_expired_bookings(now=base_now)

    snapshot = metrics_service.snapshot()

    assert snapshot["booking.success"] >= 2
    assert snapshot["booking.conflict"] == 1
    assert snapshot["booking.cancelled"] == 1
    assert snapshot["auto_release.triggered"] == 1
