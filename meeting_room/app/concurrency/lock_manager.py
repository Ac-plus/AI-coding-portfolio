from collections.abc import Iterator
from contextlib import contextmanager
from threading import RLock
import time


class LockManager:
    def __init__(self) -> None:
        self._registry_lock = RLock()
        self._locks: dict[str, RLock] = {}

    def _get_lock(self, resource_id: str) -> RLock:
        with self._registry_lock:
            if resource_id not in self._locks:
                self._locks[resource_id] = RLock()
            return self._locks[resource_id]

    @contextmanager
    def acquire_resources(
        self,
        resource_ids: list[str] | tuple[str, ...],
        timeout: float | None = None,
    ) -> Iterator[None]:
        ordered_ids = sorted(set(resource_ids))
        acquired: list[RLock] = []
        start = time.monotonic()

        try:
            for resource_id in ordered_ids:
                lock = self._get_lock(resource_id)
                if timeout is None:
                    locked = lock.acquire()
                else:
                    remaining = timeout - (time.monotonic() - start)
                    if remaining <= 0:
                        locked = False
                    else:
                        locked = lock.acquire(timeout=remaining)
                if not locked:
                    raise TimeoutError(f"Failed to acquire lock for {resource_id}.")
                acquired.append(lock)
            yield
        finally:
            for lock in reversed(acquired):
                lock.release()

    @contextmanager
    def acquire_booking_flow(self, room_id: str, timeout: float | None = None) -> Iterator[None]:
        resources = [f"file:bookings", f"room:{room_id}"]
        with self.acquire_resources(resources, timeout=timeout):
            yield
