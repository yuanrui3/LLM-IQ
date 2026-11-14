import unittest

from iqaudit.parse import parse_estimate


class ParseTest(unittest.TestCase):
    def check(self, text, estimate, method, declined=False, low=None, high=None):
        p = parse_estimate(text)
        self.assertEqual(p.method, method, text)
        self.assertEqual(p.declined, declined, text)
        if estimate is None:
            self.assertIsNone(p.estimate, text)
        else:
            self.assertAlmostEqual(p.estimate, estimate, delta=0.2, msg=text)
        if low is not None:
            self.assertEqual((p.low, p.high), (low, high), text)

    def test_format_line(self):
        self.check("Thoughtful writer.\nESTIMATE: 124 | RANGE: 115-132", 124, "format", low=115, high=132)

    def test_format_line_dash_and_tilde(self):
        self.check("ESTIMATE: ~118 | RANGE: 110–126", 118, "format", low=110, high=126)

    def test_last_format_line_wins(self):
        self.check("Format: ESTIMATE: 100 | RANGE: 90-110\n...\nESTIMATE: 131 | RANGE: 125-138", 131, "format")

    def test_format_none(self):
        self.check("Not possible from this.\nESTIMATE: NONE", None, "format_none", declined=True)

    def test_out_of_range_number_is_not_an_estimate(self):
        self.check("ESTIMATE: 999", None, "unparsed")

    def test_iq_range_fallback(self):
        self.check("Your IQ is likely in the 115-125 range.", 120, "fallback_iq", low=115, high=125)

    def test_iq_point_fallback(self):
        self.check("My best guess is an IQ of about 118.", 118, "fallback_iq")

    def test_chinese_fallback(self):
        self.check("我觉得你的智商大约在120左右。", 120, "fallback_iq")

    def test_percentile_range(self):
        # 80th -> 112.6, 95th -> 124.7
        self.check("I'd put you around the 80th-95th percentile.", 118.65, "fallback_percentile")

    def test_decline_phrase_en(self):
        self.check("I can't reliably estimate someone's IQ from text.", None, "decline_phrase", declined=True)

    def test_decline_phrase_zh(self):
        self.check("这个我没法准确判断。", None, "decline_phrase", declined=True)

    def test_unparsed(self):
        self.check("Interesting messages!", None, "unparsed")


if __name__ == "__main__":
    unittest.main()
