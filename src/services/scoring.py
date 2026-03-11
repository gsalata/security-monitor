def compute_situation_score(camera_activity: float, traffic_jam: float, weather_risk: float, news_tension: float, threat_risk: float) -> float:
    score = (
        camera_activity * 0.30
        + traffic_jam * 0.20
        + weather_risk * 0.20
        + news_tension * 0.25
        + threat_risk * 0.05
    )
    return round(max(0.0, min(100.0, score)), 2)
