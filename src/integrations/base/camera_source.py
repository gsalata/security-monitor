from abc import ABC, abstractmethod

from src.models.schemas import BoundingBox, Camera


class PublicCameraSource(ABC):
    source_id: str
    display_name: str
    update_interval: int

    @abstractmethod
    async def fetch_cameras(self, bbox: BoundingBox) -> list[Camera]:
        raise NotImplementedError
