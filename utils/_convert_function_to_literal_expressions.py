import inspect
import re
from typing import Dict

from utils._literal_expression import LiteralExpression


def _convert_function_to_literal_expressions(function_str: str) -> Dict[str, LiteralExpression]:
    function_str = (
        function_str
        .replace("-", "+-")
        .replace("[", "")
        .replace("]", "")
        .replace(" ", "")
    )
    function_split_by_literals = function_str.split("+")
    function_as_literal_expression = {}
    for x in function_split_by_literals:
        literal_expression = LiteralExpression(expression=x)
        function_as_literal_expression[literal_expression.format] = literal_expression

    return function_as_literal_expression
