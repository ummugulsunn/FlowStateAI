"""
Simple arithmetic utilities for FlowStateAI.

Implements basic operations with Python 3.11 type hints and safe division.
"""

from __future__ import annotations

from typing import Union


Numeric = Union[int, float]


def add(a: Numeric, b: Numeric) -> float:
    """Return the sum of two numbers."""
    return float(a) + float(b)


def subtract(a: Numeric, b: Numeric) -> float:
    """Return the difference of two numbers (a - b)."""
    return float(a) - float(b)


def multiply(a: Numeric, b: Numeric) -> float:
    """Return the product of two numbers."""
    return float(a) * float(b)


def divide(a: Numeric, b: Numeric) -> float:
    """
    Return the quotient of two numbers.

    Raises:
        ValueError: If an attempt is made to divide by zero.
    """
    try:
        return float(a) / float(b)
    except ZeroDivisionError as exc:  # pragma: no cover - defensive branch
        raise ValueError("Cannot divide by zero.") from exc


__all__ = ["add", "subtract", "multiply", "divide", "Numeric"]






