from src.services.scoring import compute_situation_score


def test_compute_situation_score_range() -> None:
    score = compute_situation_score(70, 70, 70, 70, 70)
    assert 0 <= score <= 100


def test_compute_situation_score_weighted() -> None:
    score = compute_situation_score(100, 0, 0, 0, 0)
    assert score == 30.0
