"""Tests: career recommendation engine."""
import unittest
import conftest_path as cp
from career_recommender import recommend_careers
from resume_parser import extract_text, parse_resume

SKILLS = None


def sample_skills():
    p = parse_resume(extract_text("r.txt", (cp.SAMPLES / "sample_resume.txt").read_bytes()))
    return p["technical_skills"] + p["soft_skills"]


class TestRecommendations(unittest.TestCase):
    def test_top_role_for_analytics_profile(self):
        recs = recommend_careers(sample_skills(), top_n=3)
        self.assertEqual(recs[0]["role"], "Data Analyst")

    def test_scores_in_range_and_sorted(self):
        recs = recommend_careers(sample_skills(), top_n=10)
        scores = [r["fit_score"] for r in recs]
        self.assertTrue(all(0 <= s <= 100 for s in scores))
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_required_fields_present(self):
        rec = recommend_careers(sample_skills(), top_n=1)[0]
        for key in ("role", "why_it_matches", "required_technical", "required_soft",
                    "matching_skills", "missing_skills", "next_steps", "disclaimer"):
            self.assertIn(key, rec)

    def test_no_employment_guarantee(self):
        self.assertIn("do not guarantee employment", recommend_careers(["Python"], top_n=1)[0]["disclaimer"])

    def test_interest_raises_score(self):
        base = {r["role"]: r["fit_score"] for r in recommend_careers(["Python"], top_n=10)}
        boosted = {r["role"]: r["fit_score"] for r in recommend_careers(["Python"], ["cybersecurity", "security"], top_n=10)}
        self.assertGreater(boosted["Cybersecurity Analyst"], base["Cybersecurity Analyst"])

    def test_empty_skills_do_not_crash(self):
        recs = recommend_careers([], top_n=3)
        self.assertEqual(len(recs), 3)
        self.assertTrue(all(r["fit_score"] == 0 for r in recs))


if __name__ == "__main__":
    unittest.main()
