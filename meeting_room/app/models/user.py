from dataclasses import asdict, dataclass


@dataclass(slots=True)
class User:
    id: str
    name: str
    team: str

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict) -> "User":
        return cls(
            id=payload["id"],
            name=payload["name"],
            team=payload["team"],
        )
