import re
from typing import List

from pyariadne import FloatDP, dp


class LiteralExpression:
    _powers: List[float]
    _coefficients: List[float]

    def _format_expression(self, expression) -> str:
        expression = re.sub(r"/pow\((\w+),(\w+)\)", r"*pow(\1,-\2)", expression)
        expression = re.sub(r"/x(\d+)", r"*pow(x\1,-1)", expression)
        expression = re.sub(r"(\w+)\*\*(\d+)", r"pow(\1,\2)", expression)
        expression = re.sub(r"(w+)\*(d+)", r"\2*x\1", expression)

        return expression

    def _case_multiple_x(self, expression: str) -> None:
        expressions = re.split(r"\*", expression) if expression.count("x") > 1 else [expression]
        for x in expressions:
            self._case_single_x(expression=x)

    def _case_single_x(self, expression: str) -> None:
        if "x" in expression:
            index = int(re.search(r"x(\d+)", expression).group(1))
            self._coefficients[index] = 1
            self._powers[index] = 1
            if "*" in expression:
                coefficient = int(re.search(r"(-?\d+)\*", expression).group(1))
                self._coefficients[index] = coefficient
            if "pow" in expression:
                power = int(re.search(rf"pow\(x{index},(-?\d+)\)", expression).group(1))
                self._powers[index] = power
            if "sqr" in expression:
                self._powers[index] = 0.5
        else:
            if "/" in expression:
                numerator, denominator = expression.split("/")
                numerator = FloatDP(numerator, dp)
                denominator = FloatDP(denominator, dp)
                value = (numerator / denominator).value()
                self._coefficients[0] = value
            else:
                self._coefficients[0] = FloatDP(expression, dp)

    def __init__(self, n_variables: int, expression: str) -> None:
        default = [0 for _ in range(n_variables)]
        self._powers = default.copy()
        self._coefficients = default.copy()

        expression = self._format_expression(expression=expression)
        if expression.count("x") > 1:
            self._case_multiple_x(expression=expression)
        else:
            self._case_single_x(expression=expression)

    @property
    def powers(self) -> List[float]:
        return self._powers

    @property
    def coefficients(self) -> List[float]:
        return self._coefficients
