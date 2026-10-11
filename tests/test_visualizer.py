import unittest

from src.profile_language import parse_profile
from src.visualizer import to_html, to_markdown, escape, profile_title


def read(name):
    with open("tests/profiles/" + name, "r", encoding="utf-8") as file:
        return file.read()


MINIMAL = """candidate "Ana <Perez>" {
    contact { email: ana@example.com }
    skills { }
    evaluation { profile DATA_ANALYST: REJECTED }
}
"""


class TestHtml(unittest.TestCase):

    def setUp(self):
        self.html = to_html(parse_profile(read("wednesday_addams.cand")))

    def test_is_html_document(self):
        self.assertTrue(self.html.startswith("<!DOCTYPE html>"))
        self.assertIn("</html>", self.html)

    def test_personal_data(self):
        self.assertIn("<h1>Wednesday Addams</h1>", self.html)
        self.assertIn("wednesday.addams@example.com", self.html)

    def test_skills(self):
        for skill in ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"]:
            self.assertIn('<span class="skill">' + skill + "</span>", self.html)

    def test_evaluation(self):
        self.assertIn('<span class="accepted">ACCEPTED</span>', self.html)
        self.assertIn("satisfy an accepted Full Stack Developer pattern", self.html)
        self.assertEqual(self.html.count('class="rejected"'), 3)

    def test_optional_parts_missing(self):
        html = to_html(parse_profile(MINIMAL))
        self.assertNotIn("<h2>Experience</h2>", html)
        self.assertNotIn("<h2>Education</h2>", html)
        self.assertIn("No skills recognized.", html)

    def test_escape(self):
        html = to_html(parse_profile(MINIMAL))
        self.assertIn("Ana &lt;Perez&gt;", html)
        self.assertEqual(escape("a & b"), "a &amp; b")


class TestMarkdown(unittest.TestCase):

    def test_content(self):
        md = to_markdown(parse_profile(read("wednesday_addams.cand")))
        self.assertTrue(md.startswith("# Wednesday Addams"))
        self.assertIn("`JAVASCRIPT`", md)
        self.assertIn("| Full Stack Developer | **ACCEPTED** |", md)
        self.assertIn("| Data Analyst | REJECTED |", md)

    def test_titles(self):
        self.assertEqual(profile_title("DEVOPS_ENGINEER"), "DevOps Engineer")


if __name__ == "__main__":
    unittest.main()
