"""Backend logic for a simple calculator app.

This module is intentionally UI-agnostic so it can be imported by both the
Gradio frontend and unit tests without side effects.
"""

from __future__ import annotations

ALLOWED_OPERATIONS: tuple[str, ...] = ("add", "subtract", "multiply", "divide")


def parse_number(value: str | int | float) -> float:
    """Convert input to float.

    Args:
        value: A string, int, or float representing a number.

    Returns:
        The parsed float value.

    Raises:
        ValueError: If the value cannot be parsed as a number.
    """
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("invalid numeric input") from exc


def calculate(num1: str | int | float, num2: str | int | float, operation: str) -> float:
    """Perform a basic arithmetic operation on two values."""
    left = parse_number(num1)
    right = parse_number(num2)

    if operation not in ALLOWED_OPERATIONS:
        raise ValueError("unsupported operation")

    if operation == "add":
        return left + right
    if operation == "subtract":
        return left - right
    if operation == "multiply":
        return left * right
    if operation == "divide":
        if right == 0:
            raise ZeroDivisionError("division by zero")
        return left / right

    raise ValueError("unsupported operation")


def format_result(result: float) -> str:
    """Convert a numeric result to a stable display string."""
    if float(result).is_integer():
        return str(int(result))
    return str(result)
