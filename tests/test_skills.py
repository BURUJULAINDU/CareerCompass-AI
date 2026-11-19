"""Tests: skill extraction, skill-match calculation, missing skills, JD analysis."""
import unittest
import conftest_path as cp
from skill_extractor import extract_skills, get_roles
from skill_gap_analyzer import analyze_for_role, analyze_gap
from job_description import analyze_job_description

JD = """Job Title: Junior Data Analyst
Requirements:
- Bachelor's degree in Statistics, Computer Science or related field
- 1-2 years of experience with SQL and Excel
- Strong Python and data visualization skills
Nice to have:
- Tableau or Power BI
- Knowledge of A/B testing
Strong communication skills are essential."""


class TestSkillExtraction(unittest.TestCase):
    def test_technical_skills_found(self):
        r = extract_skills("I use Python, SQL and scikit-learn for machine learning.")
        for s in ("Python", "SQL", "Scikit-learn", "Machine Learning"):
            self.assertIn(s, r["technical"])

    def test_soft_skills_found(self):
        self.assertIn("Teamwork", extract_skills("Great teamwork and communication")["soft"])

    def test_java_does_not_match_javascript(self):
        r = extract_skills("Experienced in JavaScript")["technical"]
        self.assertIn("JavaScript", r)
        self.assertNotIn("Java", r)

    def test_sql_does_not_match_mysql_only(self):
        r = extract_skills("Worked with MySQL databases")["technical"]
        self.assertIn("MySQL", r)
        self.assertNotIn("SQL", r)

    def test_cpp_detected(self):
        self.assertIn("C++", extract_skills("Programming in C++ and Java")["technical"])

    def test_empty_text(self):
        self.assertEqual(extract_skills(""), {"technical": [], "soft": []})


class TestSkillGap(unittest.TestCase):
    def test_match_percentage_formula(self):
        r = analyze_gap(["Python", "SQL"], ["Python", "SQL", "Excel", "Statistics"], use_semantic=False)
        self.assertEqual(r["match_percentage"], 50.0)  # 2 / 4 x 100

    def test_missing_skills_identified(self):
        r = analyze_gap(["Python"], ["Python", "SQL", "Excel"], use_semantic=False)
        self.assertEqual(set(r["missing"]), {"SQL", "Excel"})

    def test_partial_skill_via_related(self):
        r = analyze_gap(["Power BI"], ["Data Visualization"], use_semantic=False)
        self.assertEqual(r["partial"][0]["skill"], "Data Visualization")
        self.assertEqual(r["match_percentage"], 0.0)
        self.assertEqual(r["weighted_coverage"], 50.0)

    def test_additional_skills(self):
        r = analyze_gap(["Python", "Docker"], ["Python"], use_semantic=False)
        self.assertEqual(r["additional"], ["Docker"])

    def test_case_insensitive_input(self):
        r = analyze_gap(["python", "sql"], ["Python", "SQL"], use_semantic=False)
        self.assertEqual(r["match_percentage"], 100.0)

    def test_zero_required_is_safe(self):
        self.assertEqual(analyze_gap(["Python"], [])["match_percentage"], 0.0)

    def test_disclaimer_present(self):
        self.assertIn("not a probability", analyze_gap(["Python"], ["Python"])["disclaimer"])

    def test_role_analysis_and_unknown_role(self):
        roles = get_roles()
        r = analyze_for_role(["Python", "SQL"], "Data Analyst", roles)
        self.assertEqual(r["total_required"], len(roles["Data Analyst"]["required_technical"]))
        with self.assertRaises(KeyError):
            analyze_for_role(["Python"], "Astronaut", roles)


class TestJobDescription(unittest.TestCase):
    def setUp(self):
        self.r = analyze_job_description(JD, ["Python", "SQL", "Power BI"])

    def test_title(self):
        self.assertEqual(self.r["job_title"], "Junior Data Analyst")

    def test_required_vs_preferred_split(self):
        self.assertIn("SQL", self.r["required_skills"])
        self.assertIn("Tableau", self.r["preferred_skills"])
        self.assertNotIn("Tableau", self.r["required_skills"])

    def test_education_and_experience(self):
        self.assertTrue(self.r["education_requirements"])
        self.assertTrue(any("years" in e for e in self.r["experience_requirements"]))

    def test_gap_report_and_suggestions(self):
        self.assertIn("Excel", self.r["gap"]["missing"])
        self.assertTrue(self.r["resume_suggestions"])

    def test_too_short_jd_rejected(self):
        with self.assertRaises(ValueError):
            analyze_job_description("hi", ["Python"])

    def test_jd_without_skills_rejected(self):
        with self.assertRaises(ValueError):
            analyze_job_description("We are a friendly company that loves to hire great people every year.", [])


if __name__ == "__main__":
    unittest.main()
