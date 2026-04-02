from pathlib import Path

from app.models.room import Room
from app.utils.file_utils import read_json, write_json_atomic


class RoomRepository:
    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path

    def list_rooms(self) -> list[Room]:
        payload = read_json(self.file_path, default=[])
        return [Room.from_dict(item) for item in payload]

    def get_room(self, room_id: str) -> Room | None:
        for room in self.list_rooms():
            if room.id == room_id:
                return room
        return None

    def save_rooms(self, rooms: list[Room]) -> None:
        write_json_atomic(self.file_path, [room.to_dict() for room in rooms])
