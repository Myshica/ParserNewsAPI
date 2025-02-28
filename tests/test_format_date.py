import unittest
from datetime import datetime

from test_date import convert_date_flexible


class TestConvertDateFlexible(unittest.TestCase):
    def test_time_only(self):
        """Проверка времени без даты."""
        result = convert_date_flexible("21:52")
        expected = datetime.now().strftime("%d.%m.%Y") + " 21:52"
        self.assertEqual(result, expected)

    def test_full_date_russian(self):
        """Проверка полного формата даты на русском."""
        result = convert_date_flexible("20 января 2025, 17:26")
        self.assertEqual(result, "20.01.2025 17:26")

    def test_short_month_russian(self):
        """Проверка сокращённого названия месяца на русском."""
        result = convert_date_flexible("20 янв 2025, 17:26")
        self.assertEqual(result, "20.01.2025 17:26")

    def test_iso_format_with_timezone(self):
        """Проверка формата ISO с временной зоной."""
        result = convert_date_flexible("2025-01-20T17:26:00+03:00")
        self.assertEqual(result, "20.01.2025 17:26")

    def test_iso_format_without_timezone(self):
        """Проверка формата ISO без временной зоны."""
        result = convert_date_flexible("2025-01-20T17:26:00")
        self.assertEqual(result, "20.01.2025 17:26")

    def test_dot_format(self):
        """Проверка формата с точками."""
        result = convert_date_flexible("20.01.2025 17:26")
        self.assertEqual(result, "20.01.2025 17:26")

    def test_slash_format(self):
        """Проверка формата с косой чертой."""
        result = convert_date_flexible("20/01/2025")
        self.assertEqual(result, "20.01.2025 00:00")

    def test_dash_format(self):
        """Проверка формата с дефисом."""
        result = convert_date_flexible("20-01-2025")
        self.assertEqual(result, "20.01.2025 00:00")

    def test_year_dot_format(self):
        """Проверка формата года с точками."""
        result = convert_date_flexible("2025.01.20")
        self.assertEqual(result, "20.01.2025 00:00")

    def test_only_date_russian(self):
        """Проверка только даты на русском языке."""
        result = convert_date_flexible("20 января 2025")
        self.assertEqual(result, "20.01.2025 00:00")

    def test_invalid_format(self):
        """Проверка недопустимого формата."""
        with self.assertRaises(ValueError):
            convert_date_flexible("Неверная дата")

if __name__ == "__main__":
    unittest.main()
