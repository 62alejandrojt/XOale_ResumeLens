import unittest

from src.extractor import extract, find_skills, EMAIL_RE, PHONE_RE

WEDNESDAY = """Wednesday Addams
Email: wednesday.addams@example.com
Phone: +57 300 123 4567
Location: Nevermore Academy, Jericho

Summary:
3 years of experience developing web applications.

Experience:
- Web Application Developer at Nevermore Academy Projects (3 years)

Education:
- B.Sc. in Computer Science, Nevermore Academy

Technical Skills:
JS, React.js, NodeJS, Postgres, Git.
"""


class TestContactData(unittest.TestCase):

    def setUp(self):
        self.data = extract(WEDNESDAY)

    def test_name(self):
        self.assertEqual(self.data["name"], "Wednesday Addams")

    def test_email(self):
        self.assertEqual(self.data["email"], "wednesday.addams@example.com")

    def test_phone(self):
        self.assertEqual(self.data["phone"], "+57 300 123 4567")

    def test_location(self):
        self.assertEqual(self.data["location"], "Nevermore Academy, Jericho")

    def test_years(self):
        self.assertEqual(self.data["years_experience"], 3)

    def test_invalid_email(self):
        self.assertIsNone(EMAIL_RE.search("wednesday.addams@"))

    def test_short_phone(self):
        self.assertIsNone(PHONE_RE.search("call 12345"))


class TestSections(unittest.TestCase):

    def setUp(self):
        self.data = extract(WEDNESDAY)

    def test_experience(self):
        job = self.data["experience"][0]
        self.assertEqual(job["role"], "Web Application Developer")
        self.assertEqual(job["company"], "Nevermore Academy Projects")
        self.assertEqual(job["years"], 3)

    def test_education(self):
        school = self.data["education"][0]
        self.assertEqual(school["degree"], "B.Sc. in Computer Science")
        self.assertEqual(school["institution"], "Nevermore Academy")

    def test_summary(self):
        self.assertEqual(self.data["summary"], "3 years of experience developing web applications.")

    def test_no_sections(self):
        data = extract("John Smith\nno more info")
        self.assertEqual(data["experience"], [])
        self.assertEqual(data["education"], [])


class TestSkills(unittest.TestCase):

    def test_example_from_statement(self):
        data = extract(WEDNESDAY)
        self.assertEqual(data["all_skills"], ["JS", "React.js", "NodeJS", "Postgres", "Git"])

    def test_js_not_inside_react(self):
        skills = find_skills("React.js and Node.js")
        self.assertEqual(skills["languages"], [])
        self.assertEqual(skills["frameworks"], ["React.js", "Node.js"])

    def test_java_vs_javascript(self):
        skills = find_skills("Java, JavaScript")
        self.assertEqual(skills["languages"], ["Java", "JavaScript"])

    def test_spaced_variants(self):
        skills = find_skills("Tensor Flow, Py Torch, scikit learn")
        self.assertEqual(skills["libraries"], ["Tensor Flow", "Py Torch", "scikit learn"])

    def test_sql_not_inside_postgresql(self):
        skills = find_skills("PostgreSQL")
        self.assertEqual(skills["languages"], [])
        self.assertEqual(skills["databases"], ["PostgreSQL"])

    def test_no_repeated_skills(self):
        skills = find_skills("Git, Git, Git")
        self.assertEqual(skills["tools"], ["Git"])

    def test_concepts(self):
        skills = find_skills("I build machine learning models")
        self.assertEqual(skills["concepts"], ["machine learning"])


if __name__ == "__main__":
    unittest.main()
