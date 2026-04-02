from fastapi import APIRouter, Depends

from app.api.dependencies import get_room_service
from app.schemas.room import RoomResponse
from app.services.room_service import RoomService

router = APIRouter(prefix="/api/rooms", tags=["rooms"])


@router.get("", response_model=list[RoomResponse])
def list_rooms(room_service: RoomService = Depends(get_room_service)) -> list[RoomResponse]:
    return [RoomResponse(**room.to_dict()) for room in room_service.list_rooms()]
