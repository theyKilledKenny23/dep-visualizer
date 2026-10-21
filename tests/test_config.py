import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '..', 'src')))

from src.main import (
    validate_package_name,
    validate_repository_url,
    validate_test_mode,
    validate_max_depth,
)


class TestConfigValidation(unittest.TestCase):
    """Тесты валидации конфигурации."""

    def test_valid_package_name(self):
        """Проверка корректного имени пакета."""
        validate_package_name("requests")

    def test_invalid_package_name_empty(self):
        """Проверка пустого имени пакета."""
        with self.assertRaises(SystemExit):
            validate_package_name("")

    def test_invalid_package_name_type(self):
        """Проверка неверного типа имени пакета."""
        with self.assertRaises(SystemExit):
            validate_package_name(123)

    def test_valid_repository_url(self):
        """Проверка корректного URL."""
        validate_repository_url("https://pypi.org/pypi/requests/json", False)

    def test_invalid_repository_url_no_http(self):
        """Проверка URL без http в обычном режиме."""
        with self.assertRaises(SystemExit):
            validate_repository_url("ftp://example.com", False)

    def test_valid_test_mode(self):
        """Проверка корректного режима тестирования."""
        validate_test_mode(True)
        validate_test_mode(False)

    def test_invalid_test_mode_type(self):
        """Проверка неверного типа режима тестирования."""
        with self.assertRaises(SystemExit):
            validate_test_mode("true")

    def test_valid_max_depth(self):
        """Проверка корректной глубины."""
        validate_max_depth(5)

    def test_invalid_max_depth_zero(self):
        """Проверка нулевой глубины."""
        with self.assertRaises(SystemExit):
            validate_max_depth(0)

    def test_invalid_max_depth_negative(self):
        """Проверка отрицательной глубины."""
        with self.assertRaises(SystemExit):
            validate_max_depth(-1)


if __name__ == "__main__":
    unittest.main()