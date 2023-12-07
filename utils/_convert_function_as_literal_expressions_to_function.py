from typing import Dict

from pyariadne import pow
from pyariadne import sqr

from utils._literal_expression import LiteralExpression


def _convert_function_as_literal_expressions_to_function(
    function_as_literal_expressions: Dict[str, LiteralExpression]
) -> callable:
    elements_to_add = []
    for expression in function_as_literal_expressions.values():
        coefficient = expression.coefficient
        if coefficient == 0:
            continue

        powers = expression.powers
        elements_to_multiply = [str(coefficient)] if coefficient not in [-1, 1] else []
        for i, power in powers.items():
            if power == 0:
                continue

            x_i = f"x[{i}]"
            if power == 1:
                term = x_i
            elif power == 0.5:
                term = f"sqr({x_i})"
            else:
                term = f"pow({x_i},{power})"

            term = "-" + term if coefficient == -1 else term

            elements_to_multiply.append(term)

        if not elements_to_multiply:
            elements_to_multiply = [str(coefficient)]

        elements_to_add.append("*".join(elements_to_multiply))

    function_as_string = "lambda x: [" + "+".join(elements_to_add) + "]"
    function = eval(function_as_string)

    return function
