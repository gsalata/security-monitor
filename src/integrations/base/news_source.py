from abc import ABC, abstractmethod

from src.models.schemas import BoundingBox, Event


class NewsSource(ABC):
    source_id: str

    @abstractmethod
    async def fetch_events(self, bbox: BoundingBox) -> list[Event]:
        raise NotImplementedError
