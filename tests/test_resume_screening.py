import unittest
from pathlib import Path

from app.parser import parseresume
from app.matcher import matchresumetojd


class ResumeScreeningTests(unittest.TestCase):
    def test_parser_extracts_skills_from_sample_resume(self):
        sample_path = Path(__file__).resolve().parent.parent / "sample_resumes" / "resume1.txt"
        parsed = parseresume(str(sample_path))

        self.assertIn("text", parsed)
        self.assertTrue(parsed["skills"])
        self.assertIn("python", [skill.lower() for skill in parsed["skills"]])

    def test_matcher_returns_score_and_explanation(self):
        resume_text = "Experienced Python developer with FastAPI and SQL experience."
        resume_skills = ["Python", "FastAPI", "SQL"]
        jd_text = "We need a Python developer experienced with FastAPI and REST APIs."
        required_skills = ["Python", "FastAPI", "SQL", "Git"]

        result = matchresumetojd(resume_text, resume_skills, jd_text, required_skills)

        self.assertGreaterEqual(result["matchscore"], 0)
        self.assertLessEqual(result["matchscore"], 100)
        self.assertIn("matchedskills", result)
        self.assertIn("missingskills", result)
        self.assertTrue(result["explanation"].strip())


if __name__ == "__main__":
    unittest.main()
