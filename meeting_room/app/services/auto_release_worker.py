import asyncio
from contextlib import suppress

from app.services.expiration_service import ExpirationService


class AutoReleaseWorker:
    def __init__(
        self,
        expiration_service: ExpirationService,
        interval_seconds: int = 60,
    ) -> None:
        self.expiration_service = expiration_service
        self.interval_seconds = interval_seconds
        self._stop_event = asyncio.Event()
        self._task: asyncio.Task | None = None

    @property
    def running(self) -> bool:
        return self._task is not None and not self._task.done()

    async def start(self) -> None:
        if self.running:
            return
        self._stop_event.clear()
        self._task = asyncio.create_task(self._run_loop(), name="auto-release-worker")

    async def stop(self) -> None:
        if self._task is None:
            return
        self._stop_event.set()
        self._task.cancel()
        with suppress(asyncio.CancelledError):
            await self._task
        self._task = None

    async def run_once(self) -> None:
        self.expiration_service.release_expired_bookings()

    async def _run_loop(self) -> None:
        while not self._stop_event.is_set():
            await self.run_once()
            try:
                await asyncio.wait_for(self._stop_event.wait(), timeout=self.interval_seconds)
            except TimeoutError:
                continue
