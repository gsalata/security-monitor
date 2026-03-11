#!/usr/bin/env python3
"""Offline ARGUS runner using only Python stdlib.

This is a fallback runner for environments where pip/docker are unavailable.
It serves the frontend and lightweight JSON API endpoints compatible with frontend/app.js.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
FRONTEND_DIR = ROOT / "frontend"


@dataclass
class Camera:
    id: str
    name: str
    lat: float
    lon: float
    snapshot_url: str
    is_active: bool
    last_seen: str
    tags: list[str]
    source_id: str


@dataclass
class Event:
    id: str
    title: str
    category: str
    lat: float
    lon: float
    starts_at: str
    severity: int


def _float(query: dict[str, list[str]], key: str, default: float) -> float:
    try:
        return float(query.get(key, [str(default)])[0])
    except ValueError:
        return default


def _compute_score(camera_activity: float, traffic_jam: float, weather_risk: float, news_tension: float, threat_risk: float) -> float:
    score = (
        camera_activity * 0.30
        + traffic_jam * 0.20
        + weather_risk * 0.20
        + news_tension * 0.25
        + threat_risk * 0.05
    )
    return round(max(0.0, min(100.0, score)), 2)


def _mock_cameras(min_lat: float, max_lat: float, min_lon: float, max_lon: float) -> list[dict[str, Any]]:
    now = datetime.now(timezone.utc).isoformat()
    return [
        asdict(
            Camera(
                id="mock-1",
                name="Downtown Arterial",
                lat=(min_lat + max_lat) / 2,
                lon=(min_lon + max_lon) / 2,
                snapshot_url="https://placehold.co/320x180/0d1117/58a6ff?text=Camera+1",
                is_active=True,
                last_seen=now,
                tags=["traffic", "arterial"],
                source_id="mock-city",
            )
        ),
        asdict(
            Camera(
                id="mock-2",
                name="Transit Hub",
                lat=min_lat + (max_lat - min_lat) * 0.7,
                lon=min_lon + (max_lon - min_lon) * 0.35,
                snapshot_url="https://placehold.co/320x180/0d1117/f778ba?text=Camera+2",
                is_active=True,
                last_seen=now,
                tags=["traffic", "transit"],
                source_id="mock-city",
            )
        ),
    ]


def _mock_events(min_lat: float, max_lat: float, min_lon: float, max_lon: float) -> list[dict[str, Any]]:
    center_lat = (min_lat + max_lat) / 2
    center_lon = (min_lon + max_lon) / 2
    now = datetime.now(timezone.utc)
    return [
        asdict(
            Event(
                id="evt-1",
                title="Severe rainfall advisory affecting commute",
                category="weather",
                lat=center_lat + 0.02,
                lon=center_lon - 0.01,
                starts_at=(now - timedelta(minutes=40)).isoformat(),
                severity=4,
            )
        ),
        asdict(
            Event(
                id="evt-2",
                title="Major sports event causing heavy traffic",
                category="community",
                lat=center_lat - 0.015,
                lon=center_lon + 0.025,
                starts_at=(now + timedelta(hours=1)).isoformat(),
                severity=3,
            )
        ),
    ]


class ArgusHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, directory=str(FRONTEND_DIR), **kwargs)

    def _send_json(self, payload: Any, status: int = 200) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)

        if parsed.path == "/health":
            return self._send_json({"status": "ok", "runner": "local-stdlib"})

        if parsed.path == "/api/cameras":
            min_lat = _float(query, "minLat", 40.68)
            max_lat = _float(query, "maxLat", 40.82)
            min_lon = _float(query, "minLon", -74.10)
            max_lon = _float(query, "maxLon", -73.90)
            return self._send_json(_mock_cameras(min_lat, max_lat, min_lon, max_lon))

        if parsed.path == "/api/events":
            min_lat = _float(query, "minLat", 40.68)
            max_lat = _float(query, "maxLat", 40.82)
            min_lon = _float(query, "minLon", -74.10)
            max_lon = _float(query, "maxLon", -73.90)
            return self._send_json(_mock_events(min_lat, max_lat, min_lon, max_lon))

        if parsed.path == "/api/aoi/summary":
            name = query.get("name", ["Selected AOI"])[0]
            factors = {
                "camera_component": 62.0,
                "traffic_component": 71.0,
                "weather_component": 44.0,
                "news_component": 58.0,
                "threat_component": 20.0,
            }
            score = _compute_score(
                factors["camera_component"],
                factors["traffic_component"],
                factors["weather_component"],
                factors["news_component"],
                factors["threat_component"],
            )
            return self._send_json(
                {
                    "aoi_name": name,
                    "situation_score": score,
                    "headline": "Elevated activity detected",
                    "summary": "Traffic congestion and weather advisories are jointly driving elevated risk in the selected AOI.",
                    "factors": factors,
                }
            )

        if parsed.path.startswith("/assets/"):
            self.path = parsed.path.removeprefix("/assets")
            return super().do_GET()

        if parsed.path == "/" or parsed.path == "/index.html":
            self.path = "/index.html"
            return super().do_GET()

        return super().do_GET()


def main() -> None:
    port = 8000
    server = ThreadingHTTPServer(("0.0.0.0", port), ArgusHandler)
    print(f"ARGUS local runner listening on http://0.0.0.0:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
