import unittest
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from date_rules import deadline_from_phrase


class DeadlineTests(unittest.TestCase):
    def setUp(self):
        self.tz = ZoneInfo("Asia/Yekaterinburg")
        self.now = datetime(2026, 10, 6, 17, 0, tzinfo=self.tz)

    def test_friday_forms(self):
        expected = datetime(2026, 10, 9, 18, 0, tzinfo=self.tz)

        for phrase in ("к пятнице", "в пятницу", "к пт", "к пт."):
            with self.subTest(phrase=phrase):
                self.assertEqual(
                    deadline_from_phrase(phrase, self.now),
                    expected,
                )

    def test_tomorrow(self):
        expected = datetime(2026, 10, 7, 18, 0, tzinfo=self.tz)
        self.assertEqual(
            deadline_from_phrase("завтра", self.now),
            expected,
        )

    def test_today_before_18(self):
        expected = datetime(2026, 10, 6, 18, 0, tzinfo=self.tz)
        self.assertEqual(
            deadline_from_phrase("сегодня", self.now),
            expected,
        )

    def test_today_after_18(self):
        now = self.now.replace(hour=19)
        expected = datetime(2026, 10, 7, 18, 0, tzinfo=self.tz)
        self.assertEqual(
            deadline_from_phrase("сегодня", now),
            expected
        )

    def test_relative_days(self):
        for phrase, days in (
                ("через 1 день", 1),
                ("через 3 дня", 3),
                ("через 12 дней", 12),
        ):
            with self.subTest(phrase=phrase):
                self.assertEqual(
                    deadline_from_phrase(phrase, self.now),
                    self.now + timedelta(days=days),
                )

    def test_fallback(self):
        for phrase in (None, "", "непонятный срок", "срочно"):
            with self.subTest(phrase=phrase):
                self.assertEqual(
                    deadline_from_phrase(phrase, self.now),
                    self.now + timedelta(hours=24),
                )

    def test_friday_after_18(self):
        now = datetime(2026, 10, 9, 19, 0, tzinfo=self.tz)
        expected = datetime(2026, 10, 16, 18, 0, tzinfo=self.tz)
        self.assertEqual(
            deadline_from_phrase("к пт", now),
            expected
        )


if __name__ == "__main__":
    unittest.main()
