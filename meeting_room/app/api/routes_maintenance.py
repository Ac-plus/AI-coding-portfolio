from fastapi import APIRouter, Depends

from app.api.dependencies import get_expiration_service
from app.schemas.booking import ReleaseExpiredResponse
from app.services.expiration_service import ExpirationService

router = APIRouter(prefix="/api/maintenance", tags=["maintenance"])


@router.post("/release-expired", response_model=ReleaseExpiredResponse)
def release_expired_bookings(
    expiration_service: ExpirationService = Depends(get_expiration_service),
) -> ReleaseExpiredResponse:
    released = expiration_service.release_expired_bookings()
    return ReleaseExpiredResponse(
        released_count=len(released),
        released_booking_ids=[booking.id for booking in released],
    )
