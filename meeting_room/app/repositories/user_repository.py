from pathlib import Path

from app.models.user import User
from app.utils.file_utils import read_json, write_json_atomic


class UserRepository:
    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path

    def list_users(self) -> list[User]:
        payload = read_json(self.file_path, default=[])
        return [User.from_dict(item) for item in payload]

    def get_user(self, user_id: str) -> User | None:
        for user in self.list_users():
            if user.id == user_id:
                return user
        return None

    def save_users(self, users: list[User]) -> None:
        write_json_atomic(self.file_path, [user.to_dict() for user in users])
