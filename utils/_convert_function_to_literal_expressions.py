from typing import Dict
from typing import Union

from pyariadne import Function

from utils._literal_expression import LiteralExpression


def convert_function_to_literal_expressions(f: Union[str, Function]) -> Dict[str, LiteralExpression]:
    function_str = f if isinstance(f, str) else f.__crepr__()
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
        x = x.lstrip("(").rstrip(")")
        if not x or "*0" in x or x == "0":
            continue

        literal_expression = LiteralExpression(expression=x)
        function_as_literal_expression[literal_expression.format] = literal_expression

    return function_as_literal_expression
