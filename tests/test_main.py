import os
import unittest

from src.main import file_name, process_resume, OUTPUT_DIR


class TestMain(unittest.TestCase):

    def test_file_name(self):
        self.assertEqual(file_name("Wednesday Addams"), "wednesday_addams")
        self.assertEqual(file_name("Mary-Jane  Watson!"), "mary_jane_watson")
        self.assertEqual(file_name("***"), "candidate")

    def test_full_pipeline(self):
        accepted = process_resume("tests/resumes/wednesday_addams.txt", verbose=False)
        self.assertEqual(accepted, ["FULL_STACK_DEVELOPER"])
        for ext in [".html", ".md", ".cand"]:
            self.assertTrue(os.path.exists(os.path.join(OUTPUT_DIR, "wednesday_addams" + ext)))

    def test_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            process_resume("tests/resumes/does_not_exist.txt", verbose=False)


if __name__ == "__main__":
    unittest.main()
