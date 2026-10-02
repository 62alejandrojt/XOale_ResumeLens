import unittest

from src.normalizer import tokenize, normalize_skill, normalize, sort_for_profile
from src.extractor import extract_from_file


class TestTokenize(unittest.TestCase):

    def test_dot(self):
        self.assertEqual(tokenize("React.js"), ["react", "js"])

    def test_dash_and_space(self):
        self.assertEqual(tokenize("Scikit-learn"), ["scikit", "learn"])
        self.assertEqual(tokenize("scikit learn"), ["scikit", "learn"])

    def test_slash(self):
        self.assertEqual(tokenize("CI/CD"), ["ci", "cd"])

    def test_keeps_plus_and_hash(self):
        self.assertEqual(tokenize("C++"), ["c++"])
        self.assertEqual(tokenize("C#"), ["c#"])


class TestNormalizeSkill(unittest.TestCase):

    def check(self, variants, expected):
        for raw in variants:
            self.assertEqual(normalize_skill(raw), expected, raw)

    def test_javascript(self):
        self.check(["JS", "Javascript", "JavaScript", "Java Script"], "JAVASCRIPT")

    def test_java_is_not_javascript(self):
        self.assertEqual(normalize_skill("Java"), "JAVA")

    def test_react(self):
        self.check(["React", "React.js", "ReactJS"], "REACT")

    def test_node(self):
        self.check(["NodeJS", "Node.js", "node"], "NODE_JS")

    def test_postgres(self):
        self.check(["Postgres", "PostgreSQL"], "POSTGRESQL")

    def test_scikit(self):
        self.check(["sklearn", "scikit learn", "Scikit-learn"], "SCIKIT_LEARN")

    def test_spaced_names(self):
        self.check(["Tensor Flow", "TensorFlow"], "TENSORFLOW")
        self.check(["Py Torch", "PyTorch"], "PYTORCH")

    def test_rest(self):
        self.check(["REST API", "REST APIs", "RESTful API"], "REST_API")

    def test_concept(self):
        self.check(["machine learning", "Machine-learning", "predictive models"], "MACHINE_LEARNING")

    def test_unknown(self):
        self.assertIsNone(normalize_skill("Cobol"))
        self.assertIsNone(normalize_skill("react native app"))
        self.assertIsNone(normalize_skill(""))

    def test_incomplete_variant(self):
        # "tensor" alone ends in a non final state
        self.assertIsNone(normalize_skill("Tensor"))


class TestNormalizeList(unittest.TestCase):

    def test_repeated_variants(self):
        skills, unknown = normalize(["JS", "Javascript", "Cobol"])
        self.assertEqual(skills, ["JAVASCRIPT"])
        self.assertEqual(unknown, ["Cobol"])


class TestSortForProfile(unittest.TestCase):

    def test_example_from_statement(self):
        skills, _ = normalize(["Git", "NodeJS", "JS", "Postgres", "React.js"])
        self.assertEqual(sort_for_profile(skills, "FULL_STACK_DEVELOPER"),
                         ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"])

    def test_order_does_not_matter(self):
        a, _ = normalize(["Git", "Python", "Pandas"])
        b, _ = normalize(["Pandas", "Git", "Python"])
        profile = "MACHINE_LEARNING_ENGINEER"
        self.assertEqual(sort_for_profile(a, profile), sort_for_profile(b, profile))

    def test_drops_other_skills(self):
        result = sort_for_profile(["DOCKER", "PYTHON"], "FULL_STACK_DEVELOPER")
        self.assertEqual(result, [])


class TestWithExtractor(unittest.TestCase):

    def test_mary_jane(self):
        data = extract_from_file("tests/resumes/mary_jane_watson.txt")
        skills, unknown = normalize(data["all_skills"])
        self.assertEqual(unknown, [])
        self.assertEqual(sort_for_profile(skills, "MACHINE_LEARNING_ENGINEER"),
                         ["PYTHON", "PANDAS", "NUMPY", "SCIKIT_LEARN", "TENSORFLOW",
                          "MACHINE_LEARNING", "DEEP_LEARNING", "SQL", "GIT"])


if __name__ == "__main__":
    unittest.main()
