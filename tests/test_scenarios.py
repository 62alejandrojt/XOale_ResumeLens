# End-to-end scenarios: one resume per expected situation
import unittest

from src.extractor import extract_from_file
from src.normalizer import normalize
from src.classifier import classify, accepted_profiles
from src.profile_language import build_profile_text, parse_profile


def run(name):
    data = extract_from_file("tests/resumes/" + name)
    skills, unknown = normalize(data["all_skills"])
    results = classify(skills)
    model = parse_profile(build_profile_text(data, skills, results))
    return data, skills, results, model


class TestScenario1FullStack(unittest.TestCase):
    # Wednesday: example of the statement, short skill names

    def test_result(self):
        data, skills, results, model = run("wednesday_addams.txt")
        self.assertEqual(accepted_profiles(results), ["FULL_STACK_DEVELOPER"])


class TestScenario2MLEngineer(unittest.TestCase):
    # Mary Jane: example of the statement

    def test_result(self):
        data, skills, results, model = run("mary_jane_watson.txt")
        self.assertEqual(accepted_profiles(results), ["MACHINE_LEARNING_ENGINEER"])


class TestScenario3DevOps(unittest.TestCase):
    # Bruce: abbreviations (K8s, CI/CD), no cloud skipped, two jobs

    def setUp(self):
        self.data, self.skills, self.results, self.model = run("bruce_wayne.txt")

    def test_abbreviations(self):
        self.assertIn("KUBERNETES", self.skills)
        self.assertIn("CI_CD", self.skills)

    def test_years_with_plus(self):
        self.assertEqual(self.data["years_experience"], 5)

    def test_two_jobs(self):
        self.assertEqual(len(self.model.experience.jobs), 2)
        self.assertEqual(self.model.experience.jobs[1].years, 1)

    def test_result(self):
        self.assertEqual(accepted_profiles(self.results), ["DEVOPS_ENGINEER"])


class TestScenario4DataAnalyst(unittest.TestCase):
    # Lisa: no phone, concept found in the summary

    def setUp(self):
        self.data, self.skills, self.results, self.model = run("lisa_simpson.txt")

    def test_no_phone(self):
        self.assertIsNone(self.model.contact.phone)

    def test_concept_from_summary(self):
        self.assertIn("DATA_ANALYSIS", self.skills)

    def test_result(self):
        self.assertEqual(accepted_profiles(self.results), ["DATA_ANALYST"])


class TestScenario5TwoProfiles(unittest.TestCase):
    # Hermione: mixed spelling and two accepted profiles

    def setUp(self):
        self.data, self.skills, self.results, self.model = run("hermione_granger.txt")

    def test_variants(self):
        for skill in ["SCIKIT_LEARN", "PYTORCH", "POWER_BI", "MACHINE_LEARNING"]:
            self.assertIn(skill, self.skills)

    def test_two_degrees(self):
        self.assertEqual(len(self.model.education.records), 2)

    def test_result(self):
        self.assertEqual(accepted_profiles(self.results),
                         ["MACHINE_LEARNING_ENGINEER", "DATA_ANALYST"])


class TestScenario6NoProfile(unittest.TestCase):
    # Homer: valid profile, but no pattern is satisfied

    def setUp(self):
        self.data, self.skills, self.results, self.model = run("homer_simpson.txt")

    def test_skills(self):
        self.assertEqual(self.skills, ["PHP", "JAVA", "EXCEL"])

    def test_no_education(self):
        self.assertIsNone(self.model.education)

    def test_result(self):
        self.assertEqual(accepted_profiles(self.results), [])
        # the profile is still valid and has the four results
        self.assertEqual(len(self.model.evaluation.results), 4)


if __name__ == "__main__":
    unittest.main()
