from datetime import datetime, timezone

from src.integrations.base.camera_source import PublicCameraSource
from src.models.schemas import BoundingBox, Camera


class MockCityCameraAdapter(PublicCameraSource):
    source_id = "mock-city"
    display_name = "Mock City Traffic"
    update_interval = 60

    async def fetch_cameras(self, bbox: BoundingBox) -> list[Camera]:
        now = datetime.now(timezone.utc)
        seed = [
            Camera(
                id="mock-1",
                name="Downtown Arterial",
                lat=(bbox.min_lat + bbox.max_lat) / 2,
                lon=(bbox.min_lon + bbox.max_lon) / 2,
                snapshot_url="https://placehold.co/320x180/0d1117/58a6ff?text=Camera+1",
                last_seen=now,
                tags=["traffic", "arterial"],
                source_id=self.source_id,
            ),
            Camera(
                id="mock-2",
                name="Transit Hub",
                lat=bbox.min_lat + (bbox.max_lat - bbox.min_lat) * 0.7,
                lon=bbox.min_lon + (bbox.max_lon - bbox.min_lon) * 0.35,
                snapshot_url="https://placehold.co/320x180/0d1117/f778ba?text=Camera+2",
                last_seen=now,
                tags=["traffic", "transit"],
                source_id=self.source_id,
            ),
        ]
        return seed
