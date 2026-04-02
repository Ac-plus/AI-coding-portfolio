from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.dependencies import get_auto_release_worker
from app.api.routes_bookings import router as bookings_router
from app.api.routes_metrics import router as metrics_router
from app.api.routes_maintenance import router as maintenance_router
from app.api.routes_rooms import router as rooms_router
from app.api.routes_users import router as users_router
from app.utils.logging_utils import configure_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    worker = get_auto_release_worker()
    await worker.start()
    try:
        yield
    finally:
        await worker.stop()


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(title="Meeting Room Booking System", lifespan=lifespan)

    @app.get("/health")
    def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(rooms_router)
    app.include_router(users_router)
    app.include_router(bookings_router)
    app.include_router(maintenance_router)
    app.include_router(metrics_router)

    return app


app = create_app()
