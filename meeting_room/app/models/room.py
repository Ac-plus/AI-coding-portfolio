from dataclasses import asdict, dataclass


@dataclass(slots=True)
class Room:
    id: str
    name: str
    capacity: int
    location: str

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict) -> "Room":
        return cls(
            id=payload["id"],
            name=payload["name"],
            capacity=payload["capacity"],
            location=payload["location"],
        )
