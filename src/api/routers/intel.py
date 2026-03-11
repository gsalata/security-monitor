from fastapi import APIRouter

from src.models.schemas import AOISummary
from src.services.scoring import compute_situation_score

router = APIRouter(prefix="/aoi", tags=["intelligence"])


@router.get("/summary", response_model=AOISummary)
async def summary(name: str = "Selected AOI") -> AOISummary:
    factors = {
        "camera_component": 62.0,
        "traffic_component": 71.0,
        "weather_component": 44.0,
        "news_component": 58.0,
        "threat_component": 20.0,
    }
    score = compute_situation_score(
        factors["camera_component"],
        factors["traffic_component"],
        factors["weather_component"],
        factors["news_component"],
        factors["threat_component"],
    )
    return AOISummary(
        aoi_name=name,
        situation_score=score,
        headline="Elevated activity detected",
        summary="Traffic congestion and weather advisories are jointly driving elevated risk in the selected AOI.",
        factors=factors,
    )
