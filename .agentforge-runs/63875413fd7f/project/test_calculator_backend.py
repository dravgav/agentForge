"""Unit tests for the calculator backend."""

from __future__ import annotations

import unittest

from calculator_backend import ALLOWED_OPERATIONS, calculate, format_result, parse_number


class TestCalculatorBackend(unittest.TestCase):
    def test_parse_number_with_integer_string(self) -> None:
        self.assertEqual(parse_number("42"), 42.0)

    def test_parse_number_with_float_string(self) -> None:
        self.assertEqual(parse_number("3.14"), 3.14)

    def test_parse_number_with_integer_value(self) -> None:
        self.assertEqual(parse_number(7), 7.0)

    def test_parse_number_with_invalid_string(self) -> None:
        with self.assertRaisesRegex(ValueError, "invalid numeric input"):
            parse_number("abc")

    def test_calculate_addition(self) -> None:
        self.assertEqual(calculate("2", "3", "add"), 5.0)

    def test_calculate_subtraction(self) -> None:
        self.assertEqual(calculate("10", "4", "subtract"), 6.0)

    def test_calculate_multiplication(self) -> None:
        self.assertEqual(calculate("6", "7", "multiply"), 42.0)

    def test_calculate_division(self) -> None:
        self.assertEqual(calculate("7", "2", "divide"), 3.5)

    def test_calculate_division_by_zero(self) -> None:
        with self.assertRaisesRegex(ZeroDivisionError, "division by zero"):
            calculate("7", "0", "divide")

    def test_calculate_with_unsupported_operation(self) -> None:
        with self.assertRaisesRegex(ValueError, "unsupported operation"):
            calculate("1", "2", "modulo")

    def test_format_result_with_integer_value(self) -> None:
        self.assertEqual(format_result(5.0), "5")

    def test_format_result_with_non_integer_value(self) -> None:
        self.assertEqual(format_result(3.5), "3.5")

    def test_allowed_operations_contains_expected_values(self) -> None:
        self.assertEqual(ALLOWED_OPERATIONS, ("add", "subtract", "multiply", "divide"))


if __name__ == "__main__":
    unittest.main()
