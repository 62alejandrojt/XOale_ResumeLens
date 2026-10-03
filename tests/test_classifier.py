import unittest

from src.classifier import AUTOMATA, evaluate, classify, accepted_profiles
from src.extractor import extract_from_file
from src.normalizer import normalize

FS = "FULL_STACK_DEVELOPER"
ML = "MACHINE_LEARNING_ENGINEER"
DEVOPS = "DEVOPS_ENGINEER"
DA = "DATA_ANALYST"


def accepts(profile, word):
    return AUTOMATA[profile].accepts(word)


class TestAutomatonType(unittest.TestCase):

    def test_full_stack_is_dfa(self):
        self.assertTrue(AUTOMATA[FS].is_deterministic())

    def test_ml_is_nfa(self):
        self.assertFalse(AUTOMATA[ML].is_deterministic())

    def test_devops_is_not_deterministic(self):
        self.assertFalse(AUTOMATA[DEVOPS].is_deterministic())

    def test_data_analyst_is_dfa(self):
        self.assertTrue(AUTOMATA[DA].is_deterministic())


class TestFullStack(unittest.TestCase):

    def test_statement_example(self):
        self.assertTrue(accepts(FS, ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"]))

    def test_with_rest_api(self):
        self.assertTrue(accepts(FS, ["TYPESCRIPT", "ANGULAR", "DJANGO", "MYSQL", "REST_API", "GIT"]))

    def test_several_per_group(self):
        word = ["JAVASCRIPT", "TYPESCRIPT", "REACT", "VUE", "NODE_JS", "POSTGRESQL", "MONGODB", "GIT"]
        self.assertTrue(accepts(FS, word))

    def test_missing_backend(self):
        self.assertFalse(accepts(FS, ["JAVASCRIPT", "REACT", "POSTGRESQL", "GIT"]))

    def test_missing_git(self):
        self.assertFalse(accepts(FS, ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL"]))

    def test_empty(self):
        self.assertFalse(accepts(FS, []))


class TestMLEngineer(unittest.TestCase):

    def test_statement_example(self):
        self.assertTrue(accepts(ML, ["PYTHON", "PANDAS", "TENSORFLOW", "POSTGRESQL", "GIT"]))

    def test_with_concepts(self):
        word = ["PYTHON", "NUMPY", "PYTORCH", "DEEP_LEARNING", "GIT"]
        self.assertTrue(accepts(ML, word))

    def test_missing_ml_library(self):
        self.assertFalse(accepts(ML, ["PYTHON", "PANDAS", "SQL", "GIT"]))

    def test_missing_python(self):
        self.assertFalse(accepts(ML, ["PANDAS", "TENSORFLOW", "GIT"]))


class TestDevOps(unittest.TestCase):

    def test_full_word(self):
        word = ["PYTHON", "LINUX", "DOCKER", "KUBERNETES", "JENKINS", "AWS", "GIT"]
        self.assertTrue(accepts(DEVOPS, word))

    def test_epsilon_skips_optional(self):
        # no PYTHON and no cloud
        self.assertTrue(accepts(DEVOPS, ["LINUX", "DOCKER", "CI_CD", "GITHUB"]))

    def test_missing_containers(self):
        self.assertFalse(accepts(DEVOPS, ["LINUX", "JENKINS", "GIT"]))


class TestDataAnalyst(unittest.TestCase):

    def test_only_sql_and_bi(self):
        self.assertTrue(accepts(DA, ["SQL", "POWER_BI"]))

    def test_full_word(self):
        word = ["SQL", "PYTHON", "PANDAS", "EXCEL", "TABLEAU", "DATA_ANALYSIS", "POSTGRESQL"]
        self.assertTrue(accepts(DA, word))

    def test_missing_bi_tool(self):
        self.assertFalse(accepts(DA, ["SQL", "PYTHON", "PANDAS"]))

    def test_missing_sql(self):
        self.assertFalse(accepts(DA, ["PYTHON", "EXCEL"]))


class TestClassify(unittest.TestCase):

    def test_order_from_resume_does_not_matter(self):
        a = ["GIT", "POSTGRESQL", "NODE_JS", "REACT", "JAVASCRIPT"]
        word, ok = evaluate(a, FS)
        self.assertEqual(word, ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"])
        self.assertTrue(ok)

    def test_wednesday_pipeline(self):
        data = extract_from_file("tests/resumes/wednesday_addams.txt")
        skills, _ = normalize(data["all_skills"])
        self.assertEqual(accepted_profiles(classify(skills)), [FS])

    def test_mary_jane_pipeline(self):
        data = extract_from_file("tests/resumes/mary_jane_watson.txt")
        skills, _ = normalize(data["all_skills"])
        self.assertEqual(accepted_profiles(classify(skills)), [ML])

    def test_two_profiles(self):
        skills = ["SQL", "PYTHON", "PANDAS", "SCIKIT_LEARN", "POWER_BI", "GIT"]
        self.assertEqual(accepted_profiles(classify(skills)), [ML, DA])

    def test_no_profile(self):
        self.assertEqual(accepted_profiles(classify(["PHP"])), [])


if __name__ == "__main__":
    unittest.main()
