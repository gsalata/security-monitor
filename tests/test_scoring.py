import unittest

from src.services.scoring import compute_situation_score


class ComputeSituationScoreTests(unittest.TestCase):
    def test_compute_situation_score_range(self) -> None:
        score = compute_situation_score(70, 70, 70, 70, 70)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)

    def test_compute_situation_score_weighted(self) -> None:
        score = compute_situation_score(100, 0, 0, 0, 0)
        self.assertEqual(score, 30.0)


if __name__ == "__main__":
    unittest.main()
