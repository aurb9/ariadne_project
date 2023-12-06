import inspect
import re
from typing import Dict

from utils._literal_expression import LiteralExpression


def _convert_function_to_literal_expressions(n_variables: int, f: callable) -> Dict[str, LiteralExpression]:
    function_str = inspect.getsource(f)
    lambda_match = re.search(r"lambda x: (.*)\)", function_str)
    if lambda_match:
        lambda_expression = (
            lambda_match.group(1)
            .replace("-", "+-")
            .replace("[", "")
            .replace("]", "")
            .replace(" ", "")
        )
        function_split_by_literals = lambda_expression.split("+")
    else:
        raise Exception("Function not parsable, please use the right format")

    function_as_literal_expression = {}
    for x in function_split_by_literals:
        literal_expression = LiteralExpression(expression=x)
        function_as_literal_expression[literal_expression.format] = literal_expression

    return function_as_literal_expression
