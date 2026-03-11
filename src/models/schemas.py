from datetime import datetime
from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    min_lat: float = Field(alias="minLat")
    max_lat: float = Field(alias="maxLat")
    min_lon: float = Field(alias="minLon")
    max_lon: float = Field(alias="maxLon")


class Camera(BaseModel):
    id: str
    name: str
    lat: float
    lon: float
    snapshot_url: str
    is_active: bool = True
    last_seen: datetime
    tags: list[str] = []
    source_id: str


class Event(BaseModel):
    id: str
    title: str
    category: str
    lat: float
    lon: float
    starts_at: datetime
    severity: int = Field(ge=1, le=5)


class AOISummary(BaseModel):
    aoi_name: str
    situation_score: float
    headline: str
    summary: str
    factors: dict[str, float]
