import unittest

from iqaudit.rationales import code_reply


class RationaleCodingTest(unittest.TestCase):
    def test_tags_and_disclaimer(self):
        c = code_reply(
            "The person reasons systematically about variables.\n"
            "Sophisticated vocabulary is used: amortizes, delta.\n"
            "The dialect is a linguistic style, not a cognitive indicator.\n"
            "Message 4 is a graduate-level physics abstract about Majorana states."
        )
        for tag in ("reasoning", "vocabulary", "language_form", "pasted_material", "education"):
            self.assertIn(tag, c["tags"], tag)
        self.assertIn("dialect", c["form_disclaimed"])

    def test_ordinary_saving_is_not_a_paste(self):
        c = code_reply("Plan B saves $15 a month, so it pays for itself after 20 months.")
        self.assertNotIn("pasted_material", c["tags"])

    def test_chinese_reply(self):
        c = code_reply("他的推理很清晰。虽然用了很多口语和缩写，但这不影响判断。")
        self.assertIn("reasoning", c["tags"])
        self.assertIn("language_form", c["tags"])
        self.assertTrue(c["form_disclaimed"])


if __name__ == "__main__":
    unittest.main()
