from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import get_booking_service
from app.schemas.booking import BookingCreateRequest, BookingResponse
from app.services import (
    BookingConflictError,
    BookingNotFoundError,
    BookingService,
    BookingValidationError,
    RoomNotFoundError,
)

router = APIRouter(prefix="/api/bookings", tags=["bookings"])


def _serialize_booking(booking) -> BookingResponse:
    return BookingResponse(
        id=booking.id,
        room_id=booking.room_id,
        user_id=booking.user_id,
        start_time=booking.start_time,
        end_time=booking.end_time,
        status=booking.status.value,
        created_at=booking.created_at,
        expires_at=booking.expires_at,
    )


@router.get("", response_model=list[BookingResponse])
def list_bookings(
    user_id: str | None = Query(default=None),
    room_id: str | None = Query(default=None),
    date: str | None = Query(default=None),
    include_inactive: bool = Query(default=True),
    booking_service: BookingService = Depends(get_booking_service),
) -> list[BookingResponse]:
    bookings = booking_service.list_bookings(
        user_id=user_id,
        room_id=room_id,
        booking_date=date,
        include_inactive=include_inactive,
    )
    return [_serialize_booking(booking) for booking in bookings]


@router.post("", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(
    payload: BookingCreateRequest,
    booking_service: BookingService = Depends(get_booking_service),
) -> BookingResponse:
    try:
        booking = booking_service.create_booking(
            room_id=payload.room_id,
            user_id=payload.user_id,
            start_time=payload.start_time,
            end_time=payload.end_time,
        )
    except RoomNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    except BookingConflictError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error
    except BookingValidationError as error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=error.errors) from error

    return _serialize_booking(booking)


@router.delete("/{booking_id}", response_model=BookingResponse)
def cancel_booking(
    booking_id: str,
    user_id: str | None = Query(default=None),
    booking_service: BookingService = Depends(get_booking_service),
) -> BookingResponse:
    try:
        booking = booking_service.cancel_booking(booking_id, user_id=user_id)
    except BookingNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    except BookingValidationError as error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=error.errors) from error

    return _serialize_booking(booking)
