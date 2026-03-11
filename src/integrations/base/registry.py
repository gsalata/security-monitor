import asyncio

from src.integrations.base.camera_source import PublicCameraSource
from src.integrations.base.news_source import NewsSource
from src.models.schemas import BoundingBox, Camera, Event


class SourceRegistry:
    def __init__(self) -> None:
        self._camera_sources: dict[str, PublicCameraSource] = {}
        self._news_sources: dict[str, NewsSource] = {}

    def register_camera(self, source: PublicCameraSource) -> None:
        self._camera_sources[source.source_id] = source

    def register_news(self, source: NewsSource) -> None:
        self._news_sources[source.source_id] = source

    async def get_cameras_in_bbox(self, bbox: BoundingBox) -> list[Camera]:
        batches = await asyncio.gather(*[s.fetch_cameras(bbox) for s in self._camera_sources.values()])
        return [camera for batch in batches for camera in batch]

    async def get_events_in_bbox(self, bbox: BoundingBox) -> list[Event]:
        batches = await asyncio.gather(*[s.fetch_events(bbox) for s in self._news_sources.values()])
        return [event for batch in batches for event in batch]
