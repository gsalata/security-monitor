# Watch_Dogs-Style Live Intelligence Globe
## Research & Architecture Design Document

**Classification:** Open Research / Public Architecture  
**Version:** 1.0  
**Scope:** Full-stack system design — data, ML, visualization, and ethics

---

## Table of Contents

1. [Core Vision & Guiding Principles](#1-core-vision--guiding-principles)
2. [Public Live Camera Feeds](#2-public-live-camera-feeds)
3. [Live & Interesting Data APIs](#3-live--interesting-data-apis)
4. [Threat-Intelligence Integration (High-Level)](#4-threat-intelligence-integration-high-level)
5. [3D Globe & Watch_Dogs Visualization](#5-3d-globe--watchdogs-visualization)
6. [Machine Learning & Analytics Design](#6-machine-learning--analytics-design)
7. [System Architecture & GitHub-Friendly Design](#7-system-architecture--github-friendly-design)
8. [Privacy, Ethics & Compliance](#8-privacy-ethics--compliance)

---

## 1. Core Vision & Guiding Principles

### 1.1 What We're Building

The platform — internally codename **ARGUS** (Automated Real-time Geospatial Understanding System) — is a 3D interactive intelligence dashboard that fuses legally available public data into a Palantir-meets-Watch_Dogs experience. The core interaction loop is:

1. **Explore** a 3D globe, zoom to any area of interest.
2. **Select** an AOI (polygon, rectangle, or radius).
3. **Ingest** all relevant public/open data for that AOI automatically.
4. **Analyze** using ML pipelines (vision, time-series, NLP).
5. **Visualize** patterns, anomalies, and summaries in a cinematic dashboard.

### 1.2 Non-Negotiable Legal Boundaries

Every design decision in this document respects:

- **Terms of Service** of every API, dataset, and camera feed used.
- **No scraping of private or gated streams** — only officially documented public endpoints.
- **GDPR / CCPA / applicable privacy law** — no persistent storage of identifiable individuals.
- **No intrusive probing** — cyber-intel module only looks up already-public indicators, never scans live infrastructure.
- **Attribution requirements** — all open-data licenses (CC-BY, ODbL, etc.) respected and surfaced in the UI.

### 1.3 Design Philosophy

- **Pluggable first:** Every data source is a swappable adapter, not hardcoded logic.
- **Aggregate, don't expose:** ML outputs should be crowd-level metrics (vehicle counts, activity scores), not individual tracking.
- **Fail open:** If a source is down or rate-limited, the globe degrades gracefully — it doesn't crash.
- **Async everywhere:** All data ingestion is event-driven, not blocking.

---

## 2. Public Live Camera Feeds

### 2.1 Categories of Legitimate Public Camera Sources

There are three clearly legitimate categories of public camera feeds:

**Category A — Government/Municipal Traffic Camera APIs**

These are operated by transportation agencies, DOTs, and smart-city programs. They are explicitly intended for public consumption (traffic awareness, not surveillance), and most expose official REST APIs or open-data portals.

**Category B — Tourism & Scenic Webcams**

Managed by tourism boards, ski resorts, weather stations, and media outlets. Feeds are publicly streamed, typically MJPEG or HLS. Many are aggregated by third-party directories.

**Category C — Research / Smart-City Open Data**

Academic smart-city programs (e.g., Chicago Array of Things, Santander SmartSantander) publish sensor-level data including camera metadata through controlled public APIs.

---

### 2.2 Concrete Camera Source Examples

#### 2.2.1 California 511 / Caltrans Traffic Camera API

- **Provider:** California Department of Transportation (Caltrans) via 511.org
- **Access:** `https://api.511.org/traffic/cameras?api_key={KEY}&format=json`
- **Auth:** Free API key registration at 511.org
- **Coverage:** All California state highways (~2,000+ cameras)
- **Response fields:** `id`, `name`, `description`, `latitude`, `longitude`, `imageUrl` (JPEG snapshot), `status`
- **Update frequency:** Snapshots refresh every 2–5 minutes; metadata is static.
- **License/ToS:** Free for non-commercial and research use; commercial use requires separate agreement; no resale of raw images; attribution required.
- **Pros:** Large coverage, well-documented, stable API, lat/lon included.
- **Cons:** California only; image URLs are hot-linked (no download/re-host); no video stream, only snapshots.

#### 2.2.2 Washington State DOT (WSDOT) Traffic Camera API

- **Provider:** Washington State Department of Transportation
- **Access:** `https://wsdot.wa.gov/Traffic/api/HighwayCameras/HighwayCamerasREST.svc/GetCameraAsJson?CameraID={ID}&AccessCode={KEY}`
- **Listing endpoint:** `GetCamerasAsJson` returns full list with coordinates
- **Auth:** Free key from WSDOT developer portal
- **Response fields:** `CameraID`, `Title`, `Description`, `Latitude`, `Longitude`, `ImageURL`, `IsActive`, `Region`
- **Update frequency:** Snapshots every 1–2 minutes on active cameras
- **License:** Free for public-benefit, research, and app development; attribution required; no persistent image archiving.
- **Pros:** Clean REST design; rich metadata including `Region`; very stable; good Pacific Northwest coverage.
- **Cons:** State-only; some cameras are seasonal (mountain passes).

#### 2.2.3 New York City DOT — NYC Open Data Traffic Cameras

- **Provider:** New York City Department of Transportation via NYC Open Data (Socrata platform)
- **Access:** `https://data.cityofnewyork.us/resource/i4gi-tjb9.json?$where=within_circle(the_geom,{LAT},{LON},{RADIUS})`
- **Auth:** Free Socrata API token (rate limits apply without token)
- **Response fields:** `camera_id`, `name`, `url` (JPEG snapshot), `borough`, `latitude`, `longitude`, `last_update`
- **Update frequency:** Image URLs refresh every 2 minutes; metadata daily.
- **License:** NYC Open Data license — open, attribution required, no warranty.
- **Pros:** Bounding-box / geospatial query support native to Socrata; JSON and GeoJSON formats; covers all five boroughs.
- **Cons:** Some cameras may have stale `last_update` values; URLs occasionally break during maintenance.

#### 2.2.4 511NY Traffic Camera API (New York Statewide)

- **Provider:** 511NY (NYSDOT / MTA)
- **Access:** `https://511ny.org/api/getcameras?key={API_KEY}&format=json`
- **Auth:** Free key via 511NY developer portal
- **Response fields:** `ID`, `Name`, `Latitude`, `Longitude`, `Url` (snapshot JPEG), `Disabled`
- **Update frequency:** Snapshots every 3 minutes; some higher-priority cameras every 1 minute.
- **License:** Free developer use; no redistribution of raw feeds; attribution required.
- **Pros:** Complements NYC DOT with state highway coverage; same 511 family as California.
- **Cons:** Coverage density drops sharply outside major corridors.

#### 2.2.5 Transport for London (TfL) Camera Data

- **Provider:** Transport for London Unified API
- **Access:** `https://api.tfl.gov.uk/Place?type=JamCam&lat={LAT}&lon={LON}&radius={R}&app_key={KEY}`
- **Auth:** Free app key via TfL API portal
- **Response fields:** `id`, `commonName`, `lat`, `lon`, `additionalProperties` (including image URLs)
- **Update frequency:** Snapshots every 1 minute for JamCam; metadata near-real-time via TfL feeds.
- **License:** TfL Open Data License — commercial and non-commercial use permitted with attribution; no re-streaming.
- **Pros:** Well-structured, consistent API; genuine near-real-time; London coverage is excellent; good metadata quality.
- **Cons:** London-centric; camera images are small (thumbnail resolution by default).

#### 2.2.6 Windy.com / Webcams.travel Public API

- **Provider:** Windy (webcams.travel) — an aggregator of tourism and scenic webcams
- **Access:** `https://api.windy.com/webcams/api/v3/webcams?lat={LAT}&lng={LON}&radius={KM}&include=location,urls,player&limit=50`
- **Auth:** Free tier API key (1,000 calls/day); paid tiers for higher volume
- **Response fields:** `webcamId`, `title`, `status`, `location.latitude`, `location.longitude`, `location.city`, `location.country`, `urls.current.preview` (thumbnail JPEG), `urls.current.full` (embed player URL)
- **Update frequency:** Varies by source cam — typically 5–30 minutes for snapshots.
- **License:** Free tier for non-commercial; commercial use requires paid plan; no re-hosting of images; no scraping beyond API.
- **Pros:** Global coverage (millions of cams); geospatial radius query; rich location metadata; covers tourist-facing cams not in any government API.
- **Cons:** Variable quality and uptime (third-party cameras); thumbnails may lag; free tier rate limits are tight.

---

### 2.3 Generic `PublicCameraSource` Interface Design

The following interface captures the essential contract every camera adapter must fulfill:

```
Interface: PublicCameraSource

Properties:
  sourceId: string          -- Unique identifier (e.g., "caltrans-511", "tfl-jamcam")
  displayName: string       -- Human-readable label for UI
  region: GeoRegion         -- Approximate bounding box of coverage
  updateInterval: number    -- Seconds between image refreshes
  license: LicenseInfo      -- Attribution text, URL, commercial flag

Methods:
  fetchCameras(bbox: BoundingBox): Promise<Camera[]>
    -- Returns all cameras within bounding box

  fetchCameraById(id: string): Promise<Camera>
    -- Returns single camera with full metadata

  fetchSnapshot(camera: Camera): Promise<ImageSnapshot>
    -- Returns current JPEG snapshot URL or binary blob

Types:
  Camera {
    id: string
    name: string
    description?: string
    lat: number
    lon: number
    snapshotUrl: string
    streamUrl?: string        -- HLS/RTSP if available
    isActive: boolean
    lastSeen: Date
    tags: string[]            -- ["traffic", "highway", "scenic", etc.]
    sourceId: string          -- Back-reference to owning source
  }

  ImageSnapshot {
    cameraId: string
    capturedAt: Date
    url?: string              -- Hot-link if allowed
    blob?: ArrayBuffer        -- Downloaded bytes if hot-linking prohibited
    width: number
    height: number
  }

  BoundingBox {
    minLat: number
    maxLat: number
    minLon: number
    maxLon: number
  }
```

**Concrete adapters** would live at `src/integrations/cameras/<source>/index.ts`, each implementing this interface. The `CameraSourceRegistry` singleton holds all registered adapters and provides a unified `getCamerasInBBox(bbox)` method that fans out to all registered sources and merges results.

---

## 3. Live & Interesting Data APIs

### 3.1 Traffic and Mobility

#### 3.1.1 511 Regional Traffic Feeds (Nationwide US)

The 511 program is a federally encouraged but state-operated system. Each state runs its own API under a common convention.

- **Key state APIs:** California (api.511.org), New York (511ny.org/api), Oregon (tripcheck.com/api), Florida (fl511.com)
- **Common endpoints:** `/traffic/events` (incidents), `/traffic/segments` (speed/flow by road segment), `/traffic/cameras`
- **AOI query:** Most support bounding box via `?bbox={minLon},{minLat},{maxLon},{maxLat}` parameters.
- **Data format:** JSON with GeoJSON geometry; some older implementations return XML.
- **Real-time capability:** Incidents typically update every 1–5 minutes; speed segments every 5 minutes.
- **Why it's interesting:** A sudden cluster of incidents in an AOI is a strong signal of a real event — accident, protest, road closure. Combining incident count spikes with camera activity creates compelling situational awareness.

#### 3.1.2 HERE Traffic API

- **Provider:** HERE Technologies
- **Access:** `https://data.traffic.hereapi.com/v7/flow?locationReferencing=shape&in=bbox:{W,S,E,N}&apiKey={KEY}`
- **Auth:** Free tier (250,000 API calls/month for flow/incidents); credit card required for higher tiers.
- **Data available:** Traffic flow speed vs. free-flow speed per road segment, jam factor (0–10), traffic incidents (geo + category + description).
- **AOI query:** Native bounding box parameter; also supports corridor and circle queries.
- **Real-time:** Flow updates every 5 minutes; incidents near-real-time.
- **Why it's interesting:** Jam factor is a single scalar that cleanly maps to visual intensity overlays. It's ideal for heatmap rendering on the globe.

#### 3.1.3 GTFS-Realtime

- **What it is:** An open protocol from Google for publishing real-time transit data — vehicle positions, service alerts, and trip updates.
- **Access:** Each transit agency publishes its own GTFS-RT feed. Aggregators exist:
  - Transitland (transit.land/feeds) — directory of GTFS-RT feeds worldwide with a unified query API.
  - OpenMobilityData (transitfeeds.com) — similar directory.
- **Transitland API example:** `https://transit.land/api/v2/rest/feeds?bbox={W,S,E,N}&api_key={KEY}` returns feeds in a bounding box; you then fetch each feed's `realtime_urls`.
- **Data format:** Protocol Buffers (binary); libraries exist in Python, JavaScript, Go to parse.
- **Real-time:** Vehicle positions update every 15–60 seconds depending on agency.
- **Why it's interesting:** Sudden transit bunching or service alerts are strong signals of disruption. Overlaying transit density alongside traffic incidents creates a richer picture of an event's impact.

#### 3.1.4 Uber Movement (Historical Baseline Only)

- **Note:** Uber Movement provides aggregate travel time data by city zone — but it is historical (not live). It is still valuable for establishing **baseline travel time profiles** against which live HERE data can be compared to detect anomalies. Access via movement.uber.com, free with registration. Use for offline baseline computation only.

---

### 3.2 Weather and Hazards

#### 3.2.1 NOAA / National Weather Service APIs (US)

- **Primary endpoint:** `https://api.weather.gov/points/{LAT},{LON}` → returns forecast office and zone IDs  
  Then: `https://api.weather.gov/alerts/active?point={LAT},{LON}` for active alerts
- **Auth:** No API key required — completely open.
- **Data available:**
  - Active weather alerts (tornado warnings, severe thunderstorm, flood) with GeoJSON polygon geometry.
  - Hourly and 7-day forecasts.
  - Observation stations and current conditions.
- **AOI query:** Alerts endpoint supports `?area={STATE}`, `?zone={ZONE_ID}`, and `?point={LAT},{LON}`. For bounding boxes, query the zone grid.
- **Real-time:** Alerts are near-real-time (typically updated within 2 minutes of issuance).
- **Why it's interesting:** A tornado warning polygon that overlaps your AOI is an immediate, urgent overlay. Weather alerts also explain anomalies in traffic and camera activity.

#### 3.2.2 Open-Meteo (Global, Free, No Key)

- **Access:** `https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&current_weather=true&hourly=precipitation,windspeed_10m`
- **Auth:** None for the free tier (non-commercial); paid tier for commercial/high-volume.
- **Coverage:** Global, ~11km resolution.
- **Data:** Current temperature, wind speed, precipitation probability, cloud cover, weather code.
- **Real-time:** Hourly updates; current weather every 15 minutes.
- **Why it's interesting:** Heavy precipitation correlates with traffic slowdowns; extreme heat correlates with increased emergency calls. Integrating weather as a confound variable improves ML anomaly detection accuracy significantly.

#### 3.2.3 OpenWeatherMap API

- **Access:** `https://api.openweathermap.org/data/2.5/weather?lat={LAT}&lon={LON}&appid={KEY}`
- **Auth:** Free tier (1,000 calls/day, 60 calls/minute); paid tiers for higher volume.
- **Data:** Current conditions, 5-day 3-hour forecast, weather alerts (paid tier), air quality index.
- **Raster layers:** OWM provides XYZ tile layers for precipitation radar, temperature, wind — directly overlayable on map as image layers.
- **Why it's interesting:** The precipitation radar tile layer renders beautifully as a semi-transparent overlay on the globe and requires no custom rendering work.

#### 3.2.4 USGS Earthquake Hazards Program

- **Access:** `https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_hour.geojson`  
  Or with AOI: `https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&minlatitude={S}&maxlatitude={N}&minlongitude={W}&maxlongitude={E}&starttime={ISO}&endtime={ISO}`
- **Auth:** None — fully public.
- **Data:** GeoJSON FeatureCollection of earthquakes with magnitude, depth, and time.
- **Real-time:** Hourly and minute feeds available.
- **Why it's interesting:** An M4.0+ earthquake near your AOI is a life-safety event that immediately explains anomalies in every other signal.

---

### 3.3 Events and News

#### 3.3.1 NewsAPI

- **Access:** `https://newsapi.org/v2/everything?q={QUERY}&from={ISO_DATE}&sortBy=publishedAt&apiKey={KEY}`
- **Auth:** Free tier (100 requests/day, no commercial use); paid from $449/month.
- **AOI query:** Not geospatial natively — must use city/region names as query terms. Workaround: use city name, county name, or notable landmarks as `q` parameters.
- **Data:** Article title, description, URL, source, publication time, author.
- **Real-time:** Articles indexed within minutes of publication for major sources.
- **Why it's interesting:** Rapidly accumulating articles about a specific neighborhood signal an unfolding event. The NLP pipeline can geolocate extracted entities and pin stories to the globe.
- **Limitations:** Free tier is very restrictive; headline-only without paid plan; not truly geospatial.

#### 3.3.2 GDELT Project (Global Event Database — Free, Geospatial)

- **What it is:** GDELT monitors broadcast, print, and web news worldwide and codes every event using the CAMEO conflict event taxonomy. Updated every 15 minutes.
- **Access (via Google BigQuery):** `SELECT * FROM gdeltproject.gdeltv2.events WHERE ActionGeo_Lat BETWEEN {S} AND {N} AND ActionGeo_Long BETWEEN {W} AND {E} AND SQLDATE >= {DATE}`
- **Alternative access:** Daily and 15-minute CSV files at `http://data.gdeltproject.org/gdeltv2/` — downloadable, parseable without BigQuery.
- **Data:** Event type (protest, arrest, attack, meeting), actor names, location (lat/lon), article URL, tone score, goldstein scale.
- **Real-time:** 15-minute update cycle.
- **Why it's interesting:** GDELT is the gold standard for geospatially-aware news event detection. A spike in protest-coded events (CAMEO codes 14x) in your AOI is an immediate intelligence signal. The tone score (-100 to +100) can be aggregated to generate an "AOI tension score."

#### 3.3.3 PredictHQ Events API

- **Access:** `https://api.predicthq.com/v1/events/?within={RADIUS}@{LAT},{LON}&start.gte={ISO}&category=concerts,sports,community,disasters`
- **Auth:** Free tier (1,000 events/month); paid tiers scale to millions.
- **Data:** Event title, category, start/end time, predicted attendance (PHQ rank 0–90), precise geolocation, venue name.
- **Real-time:** Events are scraped and verified; major concerts/sports events appear weeks in advance; breaking events (disasters) appear within hours.
- **Why it's interesting:** Knowing that a 70,000-person concert starts in 2 hours in your AOI explains every traffic and camera anomaly in the next 4 hours. Attendance-weighted event overlays are visually powerful.

#### 3.3.4 OpenStreetMap Overpass API (Points of Interest & Events Infrastructure)

- **Access:** Overpass QL queries via `https://overpass-api.de/api/interpreter`
- **Example query:** Find all venues in a bounding box: `[out:json]; node["amenity"="stadium"](S,W,N,E); out;`
- **Auth:** None — public service. Rate limits apply; mirror to your own instance for production.
- **Data:** OSM nodes, ways, relations — venue names, types, addresses, capacity metadata where tagged.
- **Why it's interesting:** A venue overlay lets the system correlate scheduled events (from PredictHQ) with physical locations (from OSM) to render a grounded event layer on the globe.

---

### 3.4 Social / Open Web Signals

**Recommendation: Start with GDELT + RSS; defer social APIs.**

The current social media API landscape is highly restrictive post-2023:

- **Twitter/X API v2 Basic tier** ($100/month) provides limited read access. The free tier is essentially unusable for geospatial queries. The filtering stream endpoint supports keyword and geo bounding box (app_id location radius), but geographic filtering quality is poor. Not recommended for initial builds.
- **Reddit Data API** allows read access to subreddits and search by keyword. City-specific subreddits (r/NYC, r/chicago) are useful proxies for local sentiment but require manual subreddit curation and have no geospatial query support.
- **Bluesky (AT Protocol)** — emerging; the Firehose API is fully open, but geospatial filtering requires NLP post-processing. Worth monitoring.

**Recommended starting approach:** Use GDELT (which already processes social signals into structured events) plus curated RSS feeds from local news outlets, indexed by geography. This provides equivalent signal with far lower complexity and legal risk.

---

## 4. Threat-Intelligence Integration (High-Level)

### 4.1 Representative Commercial Threat-Intel Platforms

**This module is strictly passive.** It only performs lookups of indicators (IPs, domains, hashes) that already appear in publicly available text (news articles, CISA advisories, public threat reports). It never initiates scans or probes.

#### 4.1.1 VirusTotal API

- **Provider:** Google / VirusTotal
- **API:** `https://www.virustotal.com/api/v3/domains/{DOMAIN}` or `/ip_addresses/{IP}`
- **Auth:** Free API key (500 lookups/day, 4 req/min); Enterprise tier for higher volume.
- **Data returned:** Aggregated scan results from 70+ antivirus/threat engines, community votes, WHOIS, passive DNS, related files/URLs, threat category labels.
- **ToS constraint:** Lookup only — never submit data that isn't yours or isn't public. No bulk automated scraping beyond rate limits.
- **Integration model:** The NLP pipeline extracts domain/IP/URL entities from news articles and advisories. These extracted indicators are queued and looked up asynchronously.

#### 4.1.2 Recorded Future (Threat Intelligence, Israel-adjacent leadership)

- **Provider:** Recorded Future (owned by Mastercard; leadership includes Israeli cybersecurity veterans)
- **API:** Enterprise-only. `https://api.recordedfuture.com/v2/{entity_type}/{entity}` for risk scores on IPs, domains, hashes, CVEs.
- **Data returned:** Risk score (0–100), evidence strings (why it's risky), links to threat actor profiles, MITRE ATT&CK tactic alignment.
- **ToS:** Commercial license required. No free tier. Academic access via their University program.
- **Integration model:** Suitable as a premium plugin. The system would check Recorded Future only for indicators scoring above a threshold from VirusTotal.

#### 4.1.3 AlienVault OTX (Open Threat Exchange)

- **Provider:** AT&T Cybersecurity / AlienVault
- **API:** `https://otx.alienvault.com/api/v1/indicators/domain/{DOMAIN}/general` — completely free.
- **Auth:** Free API key (open registration).
- **Data returned:** Pulse count (how many threat reports reference this indicator), malware families, geo (country of origin), threat category, associated CVEs.
- **Why it's recommended for initial build:** Entirely free, no commercial restrictions for lookup, large community database, reliable uptime.
- **Integration model:** First-pass lookup for all extracted indicators. Escalate to VirusTotal or Recorded Future only for high-pulse indicators.

#### 4.1.4 Israeli Vendors (Public API Information)

- **Check Point ThreatCloud:** Check Point's threat intelligence layer. Public API access requires a Check Point account/license. The ThreatCloud API accepts IP, URL, and file hashes and returns reputation scores. Not publicly documented for free access — partner or commercial relationship required.
- **Cyberint (formerly IntSights):** Israeli threat intelligence firm. API is enterprise-only; focuses on dark web monitoring and brand protection. No free tier. Relevant for an enterprise version of ARGUS.
- **KELA Cybercrime Intelligence:** Israeli firm specializing in dark-web monitoring. API access is commercial. Relevant only if the cyber-intel module is scoped to track specific organizational threat exposure.

**Recommendation for initial build:** AlienVault OTX + VirusTotal free tier. Design the `ThreatIntelSource` interface so paid enterprise sources can be plugged in later without changing core logic.

---

### 4.2 Integration Architecture for Cyber-Intel Module

The cyber-intel module operates as a **passive enrichment layer**:

```
News / Advisories → NLP Extraction → Indicator Queue → Threat Lookup → Enriched Entity Store

Rules:
  - Only indicators found in public text are ever looked up.
  - No port scanning, no DNS brute-forcing, no WHOIS bulk queries.
  - All lookups are read-only GET requests to documented APIs.
  - Indicators are de-duplicated and cached (24h TTL) to respect rate limits.
  - If an indicator's reputation lookup fails (rate limit, API down), 
    it is silently dropped — never retried aggressively.
```

The `ThreatIntelSource` interface:

```
Interface: ThreatIntelSource
  lookup(indicator: Indicator): Promise<ThreatProfile | null>

Types:
  Indicator {
    type: "ip" | "domain" | "url" | "hash"
    value: string
    seenInSource: string    -- URL of article where found
    extractedAt: Date
  }
  ThreatProfile {
    indicator: Indicator
    riskScore: number       -- 0-100
    categories: string[]    -- ["malware", "phishing", "c2", etc.]
    confidence: number      -- 0-1
    reportCount: number
    lastSeen: Date
    source: string          -- "otx" | "virustotal" | "recorded-future"
  }
```

---

## 5. 3D Globe & Watch_Dogs Visualization

### 5.1 3D Globe Engine Comparison

#### 5.1.1 CesiumJS

- **What it is:** The most mature open-source 3D globe library. Powers NASA's WorldWind successor, multiple defense and GIS applications.
- **License:** Apache 2.0 — fully open, commercial use permitted.
- **Capabilities:**
  - Smooth zoom from deep space to street-level (WGS84 ellipsoid, physically accurate).
  - Native 3D Tiles support — the standard format for large-scale 3D city models.
  - CZML format for animated data overlays.
  - Terrain from Cesium Ion (commercial) or open sources (OpenTopography, SRTM via Cesium terrain format).
  - Time-dynamic visualization (play/pause timelines for historical playback).
  - Clipping planes, custom shaders, GLSL support.
- **Ecosystem:** Cesium Ion (managed tiling service — free tier generous), Google Photorealistic 3D Tiles integration (via Maps API).
- **Pros:**
  - Best-in-class for true 3D globe with accurate Earth representation.
  - 3D Tiles is the industry standard — most city mesh datasets ship in this format.
  - Excellent documentation and active community.
  - Time-dynamic CZML makes animated overlays straightforward.
- **Cons:**
  - Performance with very large numbers of dynamic entities (100k+ points) requires careful management.
  - Styling customization (shaders, glows, neon effects) requires more effort than deck.gl.
  - Bundle size is large (~1.5MB minified).
- **Recommended for:** The primary globe view and any scenario requiring accurate 3D terrain + 3D city tiles.

#### 5.1.2 deck.gl + MapLibre GL JS

- **What it is:** deck.gl (Uber/vis.gl) is a WebGL2 layer framework for large-scale data visualization. MapLibre GL JS is an open-source fork of Mapbox GL JS.
- **License:** MIT (both libraries).
- **Capabilities:**
  - Exceptional performance for large datasets (millions of points via GPU instancing).
  - Rich built-in layers: HexagonLayer (3D heatmap), ScatterplotLayer, ArcLayer, TripsLayer (animated paths), H3HexagonLayer.
  - Globe projection mode added in deck.gl v8.7 — basic globe, not as polished as Cesium.
  - 3D extruded building layer via MapLibre + OSM building footprints.
  - Custom GLSL shaders via ScenegraphLayer and SolidPolygonLayer.
- **Pros:**
  - Unmatched performance for dense, animated data layers (traffic flow, pedestrian heatmaps).
  - Watch_Dogs visual effects (neon glows, wireframe city, hex grid overlays) are much easier to implement via custom layer shaders.
  - Integrates with React via `@deck.gl/react` wrapper.
  - Vector tile styling via MapLibre style spec is highly flexible.
- **Cons:**
  - Globe mode is less polished than CesiumJS (no accurate WGS84 ellipsoid physics).
  - 3D Tiles support is limited (third-party `@loaders.gl/3d-tiles`).
  - No native time-dynamic animation system — must implement manually.
- **Recommended for:** The zoomed-in city/district view with Watch_Dogs-style data overlays. Best for heatmaps, flow animations, and dense marker rendering.

#### 5.1.3 Google Maps Platform + Photorealistic 3D Tiles

- **What it is:** Google's JavaScript Maps API with the newly available Photorealistic 3D Tiles (photogrammetry meshes from aerial imagery, covering 2,500+ cities globally).
- **License:** Commercial — usage-based pricing after free tier ($200/month credit).
- **Capabilities:**
  - Photorealistic meshes that look stunning — actual building textures from street-level imagery.
  - Can be rendered in CesiumJS via `@google/earthengine` tile integration.
  - Street View imagery accessible programmatically (subject to ToS).
- **Pros:** Best visual realism for urban scenes.
- **Cons:** Not open source; cost can scale quickly with usage; data is Google-licensed, cannot be re-exported or stored.
- **Recommended for:** An optional premium visual layer in the CesiumJS scene — load Photorealistic 3D Tiles when zoomed into supported cities for the most visually impressive effect.

#### 5.1.4 Recommendation Summary

| Scenario | Recommended Stack |
|----------|-------------------|
| Global globe, AOI selection, terrain | CesiumJS (primary globe) |
| 3D city view, Watch_Dogs effects | deck.gl + MapLibre (city layer) |
| Heatmaps, flow animations, 100k+ points | deck.gl ScenegraphLayer / HexagonLayer |
| 3D city meshes (premium visual) | Google Photorealistic 3D Tiles via CesiumJS |
| Building footprints (open, global) | OSM Buildings + MapLibre extrusion |
| Camera markers on globe | CesiumJS Entity / BillboardCollection |

**Architecture decision:** Use CesiumJS as the globe shell. When the user zooms below ~2km altitude over a city, transition to a deck.gl overlay rendered in the same canvas via `@deck.gl/cesium` interop. This gives the best of both worlds.

---

### 5.2 Creating the Pseudo-3D "Hacked City" Effect

#### 5.2.1 What Is Realistically Possible Today

**Available building geometry (no special effort):**

- **OpenStreetMap Buildings (`building:height` tags):** OSM has height tags for hundreds of millions of buildings globally. Tools like `osmium-tool` can export these. MapLibre's `fill-extrusion` layer renders them as 3D polygons in seconds.
- **Microsoft Building Footprints (open dataset):** 1.2 billion building footprints worldwide, released under ODbL license. Heights are estimated via ML. Available for bulk download.
- **ESRI ArcGIS World Building Footprints:** Similar global dataset, available through ArcGIS Living Atlas (subscription).
- **OpenAerialMap + Aerialod:** For specific cities, open aerial imagery can be processed with Aerialod or PDAL to generate DSMs.
- **Google Photorealistic 3D Tiles:** As discussed — photogrammetric quality where available.
- **Terrain (DEMs):** SRTM (30m global), Copernicus DEM (10m Europe), 3DEP (1m US) — all free and processable via GDAL.

**The Watch_Dogs visual effect stack:**

1. **Base geometry:** OSM extruded buildings via MapLibre `fill-extrusion` layer.
2. **Wireframe overlay:** A second pass rendering only edges (line primitives from building polygon vertices) with additive blending.
3. **Neon edge glow:** GLSL post-processing bloom pass on the wireframe layer — achieved in Three.js with `UnrealBloomPass` or in deck.gl with a custom FramebufferLayer.
4. **Holographic shading:** Building fill material uses a Fresnel-based GLSL shader — transparent at perpendicular angles, glowing at grazing angles (like a hologram).
5. **Data nodes:** Camera positions rendered as pulsing billboard sprites (CSS animation or Three.js shader) with connecting arcs drawn via deck.gl `ArcLayer`.
6. **Activity heatmap:** `HexagonLayer` with color interpolation from teal → magenta → white based on activity score.
7. **Scan line effect:** A full-screen fragment shader post-process pass applying a moving horizontal scan line to the entire scene — instantly recognizable as the Watch_Dogs aesthetic.
8. **Ambient data streams:** `TripsLayer` animating traffic flow along road network segments — glowing particles streaming along roads.

**Implementation approach:**

- CesiumJS custom shaders via `CustomShader` API (added in Cesium 1.88).
- deck.gl custom layers using the `Layer` base class with raw WebGL2.
- Post-processing via `@react-three/postprocessing` if using Three.js interop.
- CSS filters (backdrop-filter, mix-blend-mode) for 2D UI elements to maintain the aesthetic.

#### 5.2.2 What Requires Serious Research (and Why It's Impractical)

**True real-time 3D reconstruction from arbitrary public webcams:**

- **Multi-view stereo (MVS) / Structure from Motion (SfM):** Requires overlapping camera coverage from known positions. Traffic cams are fixed but sparse — not enough overlap for MVS.
- **Neural Radiance Fields (NeRF):** Requires dense imagery from controlled capture (not streaming). Real-time NeRF rendering (Instant-NGP, Gaussian Splatting) is a research frontier even on known scenes — not usable for arbitrary live streams.
- **Monocular depth estimation:** Models like MiDaS or DPT can estimate depth from a single frame, but the output is relative (no metric scale) and too noisy for map integration.
- **Conclusion:** Do not attempt real-time 3D reconstruction from live cameras. Use pre-computed building/terrain geometry (described above) and reserve camera feeds for 2D intelligence analysis only.

---

## 6. Machine Learning & Analytics Design

### 6.1 Vision Analysis on Camera Feeds

#### 6.1.1 Model Architecture

**Object Detection (Primary):**

- **Model:** YOLOv8n or YOLOv8s (Ultralytics) — best balance of inference speed and accuracy for CPU/light GPU deployment.
- **Classes of interest:** person, car, truck, bus, motorcycle, bicycle — all available in the COCO pre-trained model.
- **Frame sampling rate:** 1 frame per 60 seconds per camera for baseline monitoring; increase to 1 frame per 10 seconds when anomaly score exceeds threshold. Never stream continuously — this would violate rate limits and generate unmanageable data.
- **Resolution:** Resize all frames to 640×640 before inference (YOLO native size). No need to store original resolution frames.

**Activity Scoring (Derived Metric):**

Instead of storing bounding box coordinates (which would constitute individual tracking), compute aggregate activity scores per frame:

```
FrameActivityScore = {
  vehicle_count: int       -- total detected vehicles in frame
  pedestrian_count: int    -- total detected persons
  bike_count: int          -- total bicycles
  heavy_vehicle_count: int -- trucks + buses
  activity_index: float    -- normalized weighted sum (0.0 – 1.0)
  captured_at: datetime
  camera_id: string
}
```

**Privacy protection rule:** Bounding box coordinates are computed and immediately discarded. Only the aggregate counts per frame are persisted. No face detection, no person re-identification, no tracking across frames.

**Optical Flow (Anomaly Detection):**

- Run Lucas-Kanade optical flow (OpenCV) on consecutive frame pairs.
- Compute mean flow magnitude as a motion intensity scalar.
- Sudden zero-flow after high-flow (camera occlusion or blackout) is itself an anomaly signal.
- Sudden very-high flow (crowd surge, fast vehicle) is flagged.

#### 6.1.2 Infrastructure

- **Inference runtime:** ONNX Runtime (CPU) for ≤10 cameras; upgrade to TensorRT (NVIDIA GPU) for 100+ cameras.
- **Worker design:** Each camera has an independent async worker that fetches snapshot, runs inference, writes score to time-series store, then sleeps until next interval.
- **Rate-limit compliance:** The scheduler enforces a minimum inter-request interval per camera based on the source's documented refresh rate. No camera is ever queried faster than its official update frequency.

---

### 6.2 Time-Series and Spatiotemporal Analytics

#### 6.2.1 Per-Camera / Per-Sensor Anomaly Detection

**Approach 1 — Rolling Z-Score (Baseline):**

For each signal (vehicle count, pedestrian count, activity index), maintain a rolling 7-day historical mean (μ) and standard deviation (σ) for the same hour-of-day and day-of-week. Anomaly score = |current - μ| / σ. Alert when score > 3.0.

**Approach 2 — Isolation Forest (Production):**

Train an Isolation Forest model per camera on 30 days of historical activity vectors. The model identifies multivariate outliers that simple Z-score misses (e.g., normal-volume but unusual mix of vehicle types). Scikit-learn's `IsolationForest` runs efficiently even on CPU. Retrain weekly on rolling 30-day window.

**Approach 3 — STL Decomposition (Trend & Seasonality Separation):**

Apply STL (Seasonal-Trend decomposition using LOESS) to split any time series into trend + seasonal + residual components. Anomaly detection on the residual component is far more sensitive than raw signal anomaly detection. Python `statsmodels.tsa.seasonal.STL` handles this with minimal configuration.

#### 6.2.2 AOI-Level Situation Score

Each AOI aggregates signals from all cameras, sensors, and data streams within its bounds into a composite **AOI Situation Score (ASS, 0–100)**:

```
ASS = weighted sum of:
  - mean_camera_activity_anomaly_score × 0.30
  - traffic_jam_factor (normalized) × 0.20
  - active_weather_alert_severity × 0.20
  - GDELT_event_tone_score × 0.15
  - active_transit_alerts_count × 0.10
  - threat_intel_risk_score × 0.05

Color mapping:
  0–20   → Green (baseline / calm)
  20–50  → Yellow (elevated activity)
  50–80  → Orange (significant event)
  80–100 → Red (critical / unusual)
```

The ASS drives the globe visualization: AOIs with high scores pulse or glow more intensely on the globe surface.

#### 6.2.3 Spatiotemporal Clustering

When multiple adjacent AOIs show simultaneous anomaly spikes, apply DBSCAN clustering (scikit-learn) on the (lat, lon, time) feature space to identify spatially coherent events. Clusters are grouped as a single "event" and surfaced to the user as a unified alert with a geographic footprint.

---

### 6.3 NLP on Text Streams

#### 6.3.1 Ingestion Pipeline

News and advisory text flows through a three-stage pipeline:

**Stage 1 — Collection:** RSS feeds, NewsAPI, GDELT, and CISA advisories are polled on their respective schedules (1–15 minutes). New articles are deduplicated by URL hash and inserted into a raw text queue.

**Stage 2 — NLP Processing:** Each article passes through:

- **Language detection:** langdetect library; non-English articles are passed through MarianMT or NLLB-200 for translation (run locally to avoid API costs and privacy issues).
- **Named Entity Recognition (NER):** spaCy `en_core_web_trf` (transformer-based) extracts PERSON, ORG, GPE (geopolitical entity), LOC, EVENT, DATE entities.
- **Geolocation:** GPE and LOC entities are resolved to coordinates via:
  - Geonames lookup (geonames.org API — free, 2,000 req/day) for city/country-level resolution.
  - Nominatim (OpenStreetMap geocoder — self-hostable, no rate limit) for street-level resolution.
- **Topic Classification:** Zero-shot classification via `facebook/bart-large-mnli` on HuggingFace classifies each article into a taxonomy (traffic, crime, weather, political, infrastructure, public health, military, sports) without requiring labeled training data.
- **Summarization:** `facebook/bart-large-cnn` generates a 2–3 sentence extractive summary of each article for display in the AOI dashboard.
- **Indicator Extraction:** Custom regex + spaCy patterns extract IPs, domains, URLs, CVE numbers, and file hashes for the cyber-intel module.

**Stage 3 — Geo-linking:** Each extracted entity with resolved coordinates is written to the `geo_entities` table with a foreign key to the source article. The map service queries this table to surface "stories near this location" for any clicked globe position.

#### 6.3.2 "What's Going On Here" Summary Generation

For a user-selected AOI, a summary generation job:

1. Retrieves all articles with extracted entities within the AOI bounds (last N hours, configurable).
2. Concatenates article summaries into a context block (truncated to model's context window).
3. Sends to an LLM (local: Llama 3.1 8B-Instruct via Ollama; or cloud: Claude API) with a prompt: *"You are a situation analyst. Given these news summaries about events in [LOCATION] in the last [N] hours, provide a 3-paragraph intelligence summary: (1) what is happening, (2) what appears to be the cause, (3) what should a field team expect."*
4. Result is displayed in the AOI Dashboard's "Intelligence Summary" panel.

---

## 7. System Architecture & GitHub-Friendly Design

### 7.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        ARGUS Platform                               │
├──────────────────────────────┬──────────────────────────────────────┤
│          Frontend            │            Backend                   │
│                              │                                      │
│  GlobeView                   │  Ingestion Workers                   │
│   └── CesiumJS               │   ├── CameraWorker (per source)      │
│   └── deck.gl overlays       │   ├── TrafficWorker                  │
│                              │   ├── NewsWorker                     │
│  AOIDashboard                │   ├── WeatherWorker                  │
│   └── Charts (Recharts/D3)   │   └── ThreatIntelWorker             │
│   └── EntityTimeline         │                                      │
│   └── IntelSummaryPanel      │  API Server (FastAPI / Python)       │
│                              │   ├── /aoi/{id}/summary              │
│  LiveSourcesPanel            │   ├── /cameras?bbox=                 │
│   └── CameraGrid             │   ├── /events?bbox=                  │
│   └── DataSourceStatus       │   └── /signals?aoi_id=               │
│                              │                                      │
│  Stack:                      │  ML Processing                       │
│   React 18 + TypeScript      │   ├── VisionPipeline (YOLOv8)        │
│   Vite (build)               │   ├── TimeSeriesPipeline             │
│   Zustand (state)            │   └── NLPPipeline (spaCy + BART)     │
│   TanStack Query (fetching)  │                                      │
│   CesiumJS                   │  Data Stores                         │
│   deck.gl                    │   ├── PostgreSQL + PostGIS            │
│   MapLibre GL JS             │   ├── TimescaleDB (time-series)      │
│                              │   └── Redis (queue + cache)          │
└──────────────────────────────┴──────────────────────────────────────┘
```

### 7.2 Frontend View Designs

#### GlobeView

The primary entry point. Full-screen CesiumJS globe with:
- AOI drawing tools (Cesium's ScreenSpaceEventHandler for polygon/circle drawing).
- Camera marker layer (BillboardCollection, LOD-managed — only show when zoom < threshold).
- Weather alert polygons (loaded from NOAA GeoJSON, rendered as SurfacePolygon with pulsing color).
- Event markers (PredictHQ events — scaled by PHQ attendance rank).
- AOI Situation Score choropleth (country/region/district polygons filled by ASS color ramp).
- "Signal lightning" — arcs connecting related events (deck.gl ArcLayer overlaid on Cesium).

#### AOIDashboard

Right-side panel, slides in when an AOI is active:
- Header: AOI name, Situation Score gauge, last-updated timestamp.
- **Timeline chart:** Multi-series line chart of all normalized signals over 24h window (Recharts).
- **Camera grid:** Thumbnail grid of cameras within AOI, updated on interval. Click to expand.
- **Event list:** Active events from PredictHQ, sorted by start time.
- **News feed:** Articles with geo-entities in AOI, clustered by topic (using UMAP + HDBSCAN on embeddings).
- **Intel summary:** LLM-generated situation summary paragraph.
- **Anomaly alerts:** List of active anomaly alerts with source, score, and first-detected time.

#### LiveSourcesPanel

Bottom drawer listing all active data sources:
- Source name, type (camera / traffic / news / weather / threat), status (live / degraded / offline), last successful fetch timestamp.
- Opens raw source inspector: clicking a camera source shows the last 5 API responses.

### 7.3 Backend Stack

**Language & Framework:** Python 3.12 + FastAPI (async, high performance, automatic OpenAPI docs).

**Database:**
- PostgreSQL 16 + PostGIS extension — geospatial indexing, spatial queries (`ST_Within`, `ST_DWithin`), and standard relational data.
- TimescaleDB extension — time-series hypertables for camera activity scores, traffic readings, weather observations. Automatic data retention policies (keep full resolution for 7 days, downsample to hourly for 90 days, daily for 2 years).
- Redis 7 — job queue (via `arq` or `Celery`), API response caching (5-minute TTL for most endpoints), snapshot URL caching.

**Ingestion Workers:** Python async workers using `asyncio` + `aiohttp` for concurrent API calls. Each worker type runs in a separate process managed by `supervisor` or a container-per-worker approach.

**ML Inference:** ONNX Runtime for YOLOv8 (CPU-based inference in a dedicated worker process). HuggingFace Transformers for NLP pipeline. Ollama for local LLM summarization.

**Scheduler:** `APScheduler` (AsyncIOScheduler) with interval-based triggers per data source.

### 7.4 Data Schema (Key Tables)

```sql
-- Geospatial: Areas of Interest
CREATE TABLE aois (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    geometry GEOMETRY(POLYGON, 4326) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by TEXT
);
CREATE INDEX ON aois USING GIST(geometry);

-- Camera registry
CREATE TABLE cameras (
    id TEXT PRIMARY KEY,            -- source_id:native_id
    source_id TEXT NOT NULL,        -- e.g. "caltrans-511"
    name TEXT,
    lat DOUBLE PRECISION NOT NULL,
    lon DOUBLE PRECISION NOT NULL,
    location GEOMETRY(POINT, 4326) GENERATED ALWAYS AS 
        (ST_SetSRID(ST_MakePoint(lon, lat), 4326)) STORED,
    snapshot_url TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    last_seen TIMESTAMPTZ,
    tags TEXT[],
    metadata JSONB
);
CREATE INDEX ON cameras USING GIST(location);

-- Camera activity time-series (TimescaleDB hypertable)
CREATE TABLE camera_activity (
    time TIMESTAMPTZ NOT NULL,
    camera_id TEXT NOT NULL REFERENCES cameras(id),
    vehicle_count INTEGER,
    pedestrian_count INTEGER,
    bike_count INTEGER,
    activity_index DOUBLE PRECISION,
    anomaly_score DOUBLE PRECISION,
    PRIMARY KEY (time, camera_id)
);
SELECT create_hypertable('camera_activity', 'time');

-- Traffic readings (TimescaleDB hypertable)
CREATE TABLE traffic_readings (
    time TIMESTAMPTZ NOT NULL,
    source_id TEXT NOT NULL,
    segment_id TEXT NOT NULL,
    location GEOMETRY(LINESTRING, 4326),
    speed_kph DOUBLE PRECISION,
    free_flow_kph DOUBLE PRECISION,
    jam_factor DOUBLE PRECISION,
    PRIMARY KEY (time, source_id, segment_id)
);
SELECT create_hypertable('traffic_readings', 'time');

-- Raw articles
CREATE TABLE articles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source TEXT NOT NULL,
    title TEXT NOT NULL,
    url TEXT UNIQUE NOT NULL,
    published_at TIMESTAMPTZ,
    ingested_at TIMESTAMPTZ DEFAULT NOW(),
    summary TEXT,
    topic_label TEXT,
    sentiment_score DOUBLE PRECISION,
    raw_content_hash TEXT      -- SHA256 of content; actual content NOT stored (copyright)
);

-- Geo-entities extracted from articles
CREATE TABLE geo_entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    article_id UUID REFERENCES articles(id),
    entity_text TEXT NOT NULL,
    entity_type TEXT NOT NULL,   -- PERSON, ORG, GPE, LOC, EVENT
    location GEOMETRY(POINT, 4326),
    confidence DOUBLE PRECISION,
    resolved_name TEXT,          -- Geonames / Nominatim canonical name
    resolved_at TIMESTAMPTZ
);
CREATE INDEX ON geo_entities USING GIST(location);

-- AOI situation scores (TimescaleDB hypertable)
CREATE TABLE aoi_scores (
    time TIMESTAMPTZ NOT NULL,
    aoi_id UUID NOT NULL REFERENCES aois(id),
    situation_score DOUBLE PRECISION,
    camera_component DOUBLE PRECISION,
    traffic_component DOUBLE PRECISION,
    weather_component DOUBLE PRECISION,
    news_component DOUBLE PRECISION,
    threat_component DOUBLE PRECISION,
    PRIMARY KEY (time, aoi_id)
);
SELECT create_hypertable('aoi_scores', 'time');

-- Threat indicators (cache of lookup results)
CREATE TABLE threat_indicators (
    indicator_value TEXT NOT NULL,
    indicator_type TEXT NOT NULL,
    first_seen_in TEXT,           -- URL of source article
    looked_up_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    risk_score DOUBLE PRECISION,
    categories TEXT[],
    source TEXT,
    expires_at TIMESTAMPTZ,
    PRIMARY KEY (indicator_value, indicator_type)
);

-- Provenance / data lineage
CREATE TABLE data_provenance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    table_name TEXT NOT NULL,
    record_id TEXT NOT NULL,
    source_id TEXT NOT NULL,
    fetched_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    api_endpoint TEXT,
    license TEXT,
    attribution TEXT
);
```

---

### 7.5 Pluggable Integration Layer

#### Directory Structure

```
argus/
├── src/
│   ├── integrations/
│   │   ├── base/
│   │   │   ├── camera_source.py       -- PublicCameraSource ABC
│   │   │   ├── traffic_source.py      -- TrafficSource ABC
│   │   │   ├── news_source.py         -- NewsSource ABC
│   │   │   ├── weather_source.py      -- WeatherSource ABC
│   │   │   └── threat_intel_source.py -- ThreatIntelSource ABC
│   │   │
│   │   ├── cameras/
│   │   │   ├── caltrans_511/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── adapter.py         -- Implements PublicCameraSource
│   │   │   │   └── config.py          -- Env vars, rate limits
│   │   │   ├── tfl_jamcam/
│   │   │   ├── wsdot/
│   │   │   ├── nyc_dot/
│   │   │   └── webcams_travel/
│   │   │
│   │   ├── traffic/
│   │   │   ├── here_traffic/
│   │   │   ├── ny_511/
│   │   │   └── gtfs_realtime/
│   │   │
│   │   ├── news/
│   │   │   ├── gdelt/
│   │   │   ├── newsapi/
│   │   │   └── rss_aggregator/
│   │   │
│   │   ├── weather/
│   │   │   ├── noaa_alerts/
│   │   │   ├── open_meteo/
│   │   │   └── openweathermap/
│   │   │
│   │   └── threat_intel/
│   │       ├── otx_alienvault/
│   │       ├── virustotal/
│   │       └── recorded_future/    -- Enterprise plugin
│   │
│   ├── ml/
│   │   ├── vision/
│   │   │   ├── yolo_pipeline.py
│   │   │   └── anomaly_detector.py
│   │   ├── timeseries/
│   │   │   ├── scoring.py
│   │   │   └── isolation_forest.py
│   │   └── nlp/
│   │       ├── ner_pipeline.py
│   │       ├── geo_linker.py
│   │       ├── summarizer.py
│   │       └── indicator_extractor.py
│   │
│   ├── api/
│   │   ├── routers/
│   │   │   ├── aois.py
│   │   │   ├── cameras.py
│   │   │   ├── signals.py
│   │   │   └── intel.py
│   │   └── main.py
│   │
│   └── workers/
│       ├── camera_worker.py
│       ├── traffic_worker.py
│       ├── news_worker.py
│       ├── weather_worker.py
│       ├── nlp_worker.py
│       └── ml_worker.py
│
├── frontend/
│   ├── src/
│   │   ├── views/
│   │   │   ├── GlobeView/
│   │   │   ├── AOIDashboard/
│   │   │   └── LiveSourcesPanel/
│   │   ├── layers/          -- deck.gl / CesiumJS layer components
│   │   ├── store/           -- Zustand state slices
│   │   ├── hooks/           -- TanStack Query hooks
│   │   └── styles/          -- CSS variables for Watch_Dogs theme
│   └── public/
│       └── cesium/          -- Cesium assets (copy from package)
│
├── docker/
│   ├── docker-compose.yml
│   ├── api.Dockerfile
│   ├── worker.Dockerfile
│   └── ml.Dockerfile
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── DATA_SOURCES.md      -- Per-source ToS summaries and license notes
│   └── ETHICS.md
│
├── scripts/
│   ├── seed_cameras.py      -- Populate camera registry from all sources
│   └── check_api_keys.py    -- Validate all configured API keys
│
├── .env.example             -- Template for all required API keys
├── README.md
└── CONTRIBUTING.md
```

#### Registry Pattern (for swappable adapters)

Each integration type has a Registry singleton that discovers and registers adapters at startup:

```python
# src/integrations/base/registry.py (conceptual)

class SourceRegistry:
    def __init__(self):
        self._sources: dict[str, PublicCameraSource] = {}

    def register(self, source: PublicCameraSource):
        self._sources[source.source_id] = source

    async def get_cameras_in_bbox(self, bbox: BoundingBox) -> list[Camera]:
        results = await asyncio.gather(*[
            s.fetch_cameras(bbox) for s in self._sources.values()
            if s.region.overlaps(bbox)
        ])
        return [cam for batch in results for cam in batch]

# At startup (main.py):
registry = SourceRegistry()
if settings.CALTRANS_API_KEY:
    registry.register(Caltrans511Adapter(settings.CALTRANS_API_KEY))
if settings.TFL_API_KEY:
    registry.register(TflJamcamAdapter(settings.TFL_API_KEY))
# ... etc.
```

This means adding a new city's camera API is as simple as creating a new folder under `src/integrations/cameras/`, implementing the `PublicCameraSource` ABC, and registering it in `main.py`. No changes to any core logic required.

---

## 8. Privacy, Ethics & Compliance

### 8.1 Privacy-Preserving Design Choices

**No Raw Frame Retention:**
Camera snapshots are fetched, passed to the ML pipeline, and the in-memory buffer is released. No raw images are written to disk or stored in the database. Only the aggregated activity scores are persisted. This eliminates GDPR/CCPA exposure for individuals appearing in camera footage.

**No Individual Tracking:**
The vision pipeline explicitly prohibits: face detection (no model is loaded for this), person re-identification across frames, cross-camera entity linking. Any attempt to add such capabilities through a pull request must pass a mandatory ethics review (documented in CONTRIBUTING.md).

**Minimum Data Principle:**
Each data source adapter must document the minimum fields necessary for its function. Fields not needed for the ML pipeline or the UI are dropped before storage.

**Role-Based Access Control (RBAC):**
The API requires JWT authentication. Three roles are defined:
- `viewer` — read-only access to scores, summaries, and public map data.
- `analyst` — read access to raw signals and camera activity time-series.
- `admin` — source configuration, system management.

**Audit Logging:**
All analyst and admin actions are written to an immutable audit log (Postgres append-only table with trigger). Who queried what AOI, when, is fully traceable.

### 8.2 Legal / ToS Constraints Summary

| Source Category | Key Constraints |
|-----------------|-----------------|
| 511 Camera APIs | Attribution required; no re-hosting raw images; commercial use may require separate agreement |
| TfL | Attribution required; no re-streaming |
| Webcams.travel / Windy | Commercial use requires paid plan; no scraping beyond API |
| NOAA | Fully public domain (US government work) |
| Open-Meteo | Non-commercial free; commercial requires license |
| GDELT | Open database license; free for all uses |
| NewsAPI | Free tier: non-commercial only; paid for commercial |
| PredictHQ | Free tier available; commercial requires subscription |
| OSM / Overpass | ODbL license — attribution required; share-alike for derived databases |
| VirusTotal | Free tier: non-commercial lookups only; no bulk scraping |
| AlienVault OTX | Free for all uses with API key |

**ToS Compliance Mechanisms:**
- Each adapter stores its `license` and `attribution` string, which is surfaced in the UI's "Data Sources" panel and in any exported report.
- Rate limits are enforced by the scheduler with a per-source token bucket — the system cannot be configured to exceed any source's documented rate limits.
- A startup check validates that all API keys are present and tests a single probe call to confirm ToS-compliant access before workers begin full operation.

### 8.3 GitHub Documentation Standards

**README.md must include:**
- Clear statement: "This platform uses exclusively lawfully obtained public data."
- List of all data sources with links to their respective ToS/license pages.
- Explicit prohibition: "Do not add data sources that require bypassing access controls, scraping private streams, or violating any site's terms of service."

**CONTRIBUTING.md must include:**
- "Ethics Review" gate: any new data source adapter must include a `LEGAL.md` in its directory documenting the source's ToS, rate limits, attribution requirements, and confirming public/open access.
- "Privacy Review" gate: any ML feature that processes individual-level data (faces, biometrics, re-identification) requires a documented ethics review approved by a project maintainer before merging.

**ETHICS.md must include:**
- Statement of purpose: situational awareness and research, not surveillance.
- Prohibited uses: this software must not be used to track individuals, target communities, or facilitate law enforcement surveillance without proper legal authorization.
- Contact for responsible disclosure of misuse.

---

## Appendix A: Recommended Technology Stack Summary

| Layer | Technology | License | Notes |
|-------|-----------|---------|-------|
| Frontend framework | React 18 + TypeScript | MIT | Vite for build tooling |
| 3D Globe | CesiumJS | Apache 2.0 | Primary globe renderer |
| City overlays | deck.gl | MIT | Watch_Dogs visual layers |
| Vector tiles | MapLibre GL JS | BSD-2 | Open Mapbox GL fork |
| State management | Zustand | MIT | Lightweight, async-friendly |
| Data fetching | TanStack Query | MIT | Caching + background refetch |
| Charts | Recharts | MIT | Composable, React-native |
| Backend framework | FastAPI (Python 3.12) | MIT | Async, auto-docs |
| Primary database | PostgreSQL 16 + PostGIS | PostgreSQL License | Spatial indexing |
| Time-series | TimescaleDB | Timescale License | Free for self-hosted |
| Cache / Queue | Redis 7 | BSD-3 | Pub/sub + job queue |
| Object detection | YOLOv8 (Ultralytics) | AGPL-3.0 | Commercial license available |
| NLP | spaCy + HuggingFace | MIT / Apache 2.0 | |
| Local LLM | Ollama + Llama 3.1 8B | MIT / Meta license | Self-hosted, free |
| Containerization | Docker + Compose | Apache 2.0 | |
| Reverse proxy | Caddy or Nginx | Apache 2.0 / BSD | TLS termination |

---

## Appendix B: Proof-of-Concept Build Order

For a team starting from scratch, the recommended build sequence minimizes integration risk:

1. **Sprint 1:** PostGIS + TimescaleDB schema + FastAPI skeleton + basic CesiumJS globe with OSM building extrusion. Goal: see a 3D city.
2. **Sprint 2:** Integrate one camera source (TfL or Caltrans 511). Render camera markers on globe. Snapshot display in sidebar. Goal: see real camera markers on the globe.
3. **Sprint 3:** Add NOAA weather alerts + HERE traffic flow. Render as overlays. Goal: multi-layer data on globe.
4. **Sprint 4:** AOI drawing tool. Backend AOI endpoint. AOI Dashboard panel skeleton. Goal: select an area and see its data.
5. **Sprint 5:** YOLOv8 vision pipeline on camera snapshots. Activity scores in TimescaleDB. Timeline chart in dashboard. Goal: ML data flowing into the UI.
6. **Sprint 6:** GDELT ingestion + spaCy NER + geo-linking. News feed in dashboard. Globe markers for news events. Goal: text intelligence on the map.
7. **Sprint 7:** AOI Situation Score computation. Globe AOI color coding. Anomaly detection (Z-score baseline). Goal: the globe "reacts" to what's happening.
8. **Sprint 8:** Watch_Dogs visual polish — wireframe buildings, neon edge shader, scan-line post-process, animated traffic flow via TripsLayer. Goal: it looks like Watch_Dogs.
9. **Sprint 9:** LLM summarization pipeline. Intel Summary panel. Goal: plain-English "what's happening here."
10. **Sprint 10:** AlienVault OTX integration. Threat indicator panel. Security hardening, RBAC, audit logging. Goal: production-ready.

---

*Document version 1.0 — prepared as a research and design foundation for the ARGUS platform. All APIs, technologies, and legal constraints described herein were accurate as of the document date. Verify current ToS before production deployment.*
