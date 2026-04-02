from app.models.room import Room
from app.repositories.room_repository import RoomRepository


class RoomService:
    def __init__(self, room_repository: RoomRepository) -> None:
        self.room_repository = room_repository

    def list_rooms(self) -> list[Room]:
        return self.room_repository.list_rooms()
