"""
Calculator plugin for mathematical operations.

Provides basic arithmetic and mathematical functions for agents.
"""

import logging
from typing import Union

logger = logging.getLogger(__name__)


class CalculatorPlugin:
    """Plugin for performing mathematical calculations."""

    @staticmethod
    def add(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """Add two numbers.

        Args:
            a: First number
            b: Second number

        Returns:
            Sum of a and b
        """
        result = a + b
        logger.debug(f"Calculator: {a} + {b} = {result}")
        return result

    @staticmethod
    def subtract(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """Subtract b from a.

        Args:
            a: Minuend
            b: Subtrahend

        Returns:
            Difference of a and b
        """
        result = a - b
        logger.debug(f"Calculator: {a} - {b} = {result}")
        return result

    @staticmethod
    def multiply(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """Multiply two numbers.

        Args:
            a: First number
            b: Second number

        Returns:
            Product of a and b
        """
        result = a * b
        logger.debug(f"Calculator: {a} * {b} = {result}")
        return result

    @staticmethod
    def divide(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """Divide a by b.

        Args:
            a: Dividend
            b: Divisor

        Returns:
            Quotient of a and b

        Raises:
            ValueError: If divisor is zero
        """
        if b == 0:
            raise ValueError("Division by zero is not allowed")
        result = a / b
        logger.debug(f"Calculator: {a} / {b} = {result}")
        return result

    @staticmethod
    def power(base: Union[int, float], exponent: Union[int, float]) -> Union[int, float]:
        """Raise base to the power of exponent.

        Args:
            base: Base number
            exponent: Exponent

        Returns:
            Result of base ** exponent
        """
        result = base**exponent
        logger.debug(f"Calculator: {base} ** {exponent} = {result}")
        return result

    @staticmethod
    def square_root(a: Union[int, float]) -> float:
        """Calculate square root of a.

        Args:
            a: Number to find square root of

        Returns:
            Square root of a

        Raises:
            ValueError: If a is negative
        """
        if a < 0:
            raise ValueError("Cannot calculate square root of negative number")
        result = a**0.5
        logger.debug(f"Calculator: sqrt({a}) = {result}")
        return result
