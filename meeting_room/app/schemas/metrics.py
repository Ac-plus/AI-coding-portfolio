from pydantic import BaseModel


class MetricsResponse(BaseModel):
    counters: dict[str, int]
