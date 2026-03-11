from fastapi import APIRouter, Depends

from src.api.state import get_registry
from src.models.schemas import BoundingBox, Camera

router = APIRouter(prefix="/cameras", tags=["cameras"])


@router.get("", response_model=list[Camera])
async def cameras(minLat: float, maxLat: float, minLon: float, maxLon: float, registry=Depends(get_registry)) -> list[Camera]:
    bbox = BoundingBox(minLat=minLat, maxLat=maxLat, minLon=minLon, maxLon=maxLon)
    return await registry.get_cameras_in_bbox(bbox)
