from abc import ABC, abstractmethod


class ThreatIntelSource(ABC):
    source_id: str

    @abstractmethod
    async def lookup(self, indicator: str) -> dict | None:
        raise NotImplementedError
