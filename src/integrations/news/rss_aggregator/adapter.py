from datetime import datetime, timedelta, timezone

from src.integrations.base.news_source import NewsSource
from src.models.schemas import BoundingBox, Event


class MockNewsAdapter(NewsSource):
    source_id = "mock-news"

    async def fetch_events(self, bbox: BoundingBox) -> list[Event]:
        center_lat = (bbox.min_lat + bbox.max_lat) / 2
        center_lon = (bbox.min_lon + bbox.max_lon) / 2
        now = datetime.now(timezone.utc)
        return [
            Event(
                id="evt-1",
                title="Severe rainfall advisory affecting commute",
                category="weather",
                lat=center_lat + 0.02,
                lon=center_lon - 0.01,
                starts_at=now - timedelta(minutes=40),
                severity=4,
            ),
            Event(
                id="evt-2",
                title="Major sports event causing heavy traffic",
                category="community",
                lat=center_lat - 0.015,
                lon=center_lon + 0.025,
                starts_at=now + timedelta(hours=1),
                severity=3,
            ),
        ]
