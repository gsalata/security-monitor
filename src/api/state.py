from src.integrations.base.registry import SourceRegistry
from src.integrations.cameras.mock_city.adapter import MockCityCameraAdapter
from src.integrations.news.rss_aggregator.adapter import MockNewsAdapter

registry = SourceRegistry()
registry.register_camera(MockCityCameraAdapter())
registry.register_news(MockNewsAdapter())


def get_registry() -> SourceRegistry:
    return registry
