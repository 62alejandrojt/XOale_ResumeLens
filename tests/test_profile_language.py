import unittest

from src.profile_language import (
    build_profile_text, parse_profile, validate_profile, accepted_profiles, ProfileError,
)
from src.extractor import extract_from_file
from src.normalizer import normalize
from src.classifier import classify


def read(name):
    with open("tests/profiles/" + name, "r", encoding="utf-8") as file:
        return file.read()


MINIMAL = """candidate "Ana Perez" {
    contact { email: ana@example.com }
    skills { SQL POWER_BI }
    evaluation { profile DATA_ANALYST: ACCEPTED }
}
"""


class TestValidProfiles(unittest.TestCase):

    def test_hand_written_file(self):
        model = parse_profile(read("wednesday_addams.cand"))
        self.assertEqual(model.name, "Wednesday Addams")
        self.assertEqual(model.contact.email, "wednesday.addams@example.com")
        self.assertEqual(model.experience.jobs[0].years, 3)
        self.assertEqual(model.education.records[0].institution, "Nevermore Academy")
        self.assertEqual(accepted_profiles(model), ["FULL_STACK_DEVELOPER"])

    def test_minimal_profile(self):
        # optional parts can be missing
        model = parse_profile(MINIMAL)
        self.assertIsNone(model.experience)
        self.assertEqual(model.skills.names, ["SQL", "POWER_BI"])

    def test_several_jobs(self):
        text = MINIMAL.replace("    skills", '    experience {\n'
                               '        job "Analyst" at "A" years: 1\n'
                               '        job "Senior Analyst" at "B" years: 2\n'
                               '    }\n    skills')
        model = parse_profile(text)
        self.assertEqual(len(model.experience.jobs), 2)

    def test_empty_skills_block(self):
        ok, _ = validate_profile(MINIMAL.replace("SQL POWER_BI", ""))
        self.assertTrue(ok)


class TestLexicalErrors(unittest.TestCase):

    def test_bad_email(self):
        ok, reason = validate_profile(read("invalid_email.cand"))
        self.assertFalse(ok)
        self.assertIn("Email", reason)

    def test_lowercase_skill(self):
        ok, _ = validate_profile(MINIMAL.replace("SQL", "sql"))
        self.assertFalse(ok)

    def test_unknown_status(self):
        ok, _ = validate_profile(MINIMAL.replace("ACCEPTED", "MAYBE"))
        self.assertFalse(ok)

    def test_years_not_number(self):
        text = MINIMAL.replace("    skills", '    experience { job "A" at "B" years: two }\n    skills')
        ok, _ = validate_profile(text)
        self.assertFalse(ok)


class TestSyntaxErrors(unittest.TestCase):

    def test_missing_evaluation(self):
        ok, reason = validate_profile(read("missing_evaluation.cand"))
        self.assertFalse(ok)
        self.assertIn("evaluation", reason)

    def test_missing_brace(self):
        ok, _ = validate_profile(MINIMAL.rstrip().rstrip("}"))
        self.assertFalse(ok)

    def test_wrong_block_order(self):
        text = """candidate "Ana Perez" {
    skills { SQL }
    contact { email: ana@example.com }
    evaluation { profile DATA_ANALYST: REJECTED }
}"""
        ok, _ = validate_profile(text)
        self.assertFalse(ok)

    def test_unknown_profile(self):
        ok, _ = validate_profile(MINIMAL.replace("DATA_ANALYST", "CHEF"))
        self.assertFalse(ok)


class TestExtraRules(unittest.TestCase):

    def test_repeated_skill(self):
        with self.assertRaises(ProfileError):
            parse_profile(MINIMAL.replace("SQL POWER_BI", "SQL SQL"))

    def test_repeated_profile(self):
        text = MINIMAL.replace("profile DATA_ANALYST: ACCEPTED",
                               "profile DATA_ANALYST: ACCEPTED profile DATA_ANALYST: REJECTED")
        ok, reason = validate_profile(text)
        self.assertFalse(ok)
        self.assertIn("twice", reason)


class TestGeneratedProfiles(unittest.TestCase):

    def pipeline(self, path):
        data = extract_from_file(path)
        skills, _ = normalize(data["all_skills"])
        return build_profile_text(data, skills, classify(skills))

    def test_wednesday(self):
        model = parse_profile(self.pipeline("tests/resumes/wednesday_addams.txt"))
        self.assertEqual(accepted_profiles(model), ["FULL_STACK_DEVELOPER"])
        self.assertEqual(model.contact.phone, "+57 300 123 4567")

    def test_mary_jane(self):
        model = parse_profile(self.pipeline("tests/resumes/mary_jane_watson.txt"))
        self.assertEqual(accepted_profiles(model), ["MACHINE_LEARNING_ENGINEER"])

    def test_quotes_in_text(self):
        data = {"name": 'John "JJ" Smith', "email": "jj@example.com"}
        text = build_profile_text(data, ["PYTHON"], {})
        self.assertFalse(validate_profile(text)[0])  # no results -> invalid
        results = {"DATA_ANALYST": {"result": "REJECTED"}}
        self.assertTrue(validate_profile(build_profile_text(data, ["PYTHON"], results))[0])


if __name__ == "__main__":
    unittest.main()
