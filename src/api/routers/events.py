from fastapi import APIRouter, Depends

from src.api.state import get_registry
from src.models.schemas import BoundingBox, Event

router = APIRouter(prefix="/events", tags=["events"])


@router.get("", response_model=list[Event])
async def events(minLat: float, maxLat: float, minLon: float, maxLon: float, registry=Depends(get_registry)) -> list[Event]:
    bbox = BoundingBox(minLat=minLat, maxLat=maxLat, minLon=minLon, maxLon=maxLon)
    return await registry.get_events_in_bbox(bbox)
