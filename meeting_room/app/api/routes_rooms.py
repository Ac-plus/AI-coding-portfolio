from datetime import datetime

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_room_service
from app.schemas.room import OccupancyItemResponse, RoomResponse
from app.services.room_service import RoomService

router = APIRouter(prefix="/api/rooms", tags=["rooms"])


@router.get("", response_model=list[RoomResponse])
def list_rooms(room_service: RoomService = Depends(get_room_service)) -> list[RoomResponse]:
    return [RoomResponse(**room.to_dict()) for room in room_service.list_rooms()]


@router.get("/occupancy", response_model=list[OccupancyItemResponse])
def get_room_occupancy(
    start_time: datetime = Query(...),
    end_time: datetime = Query(...),
    room_service: RoomService = Depends(get_room_service),
) -> list[OccupancyItemResponse]:
    return [
        OccupancyItemResponse(**item)
        for item in room_service.get_occupancy_status(start_time=start_time, end_time=end_time)
    ]
