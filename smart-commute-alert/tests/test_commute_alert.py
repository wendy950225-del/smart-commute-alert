import unittest

from commute_alert import build_advice


class BuildAdviceTests(unittest.TestCase):
    def test_all_conditions_normal(self):
        self.assertEqual(build_advice(32.9, 59, 99), ["✅ 各項條件正常，適合外出通勤。"])

    def test_all_thresholds_are_inclusive(self):
        advice = build_advice(33, 60, 100)
        self.assertEqual(len(advice), 3)
        self.assertIn("雨傘", advice[0])
        self.assertIn("防曬", advice[1])
        self.assertIn("口罩", advice[2])

    def test_multiple_warnings_can_appear_together(self):
        advice = build_advice(35, 80, 50)
        self.assertEqual(len(advice), 2)


if __name__ == "__main__":
    unittest.main()
