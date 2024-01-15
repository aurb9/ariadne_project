from typing import List

from pyariadne import pow
from pyariadne import Dyadic
from pyariadne import sqr

from utils._coordinate import Coordinate

ONE = Dyadic("1")


def convert_coordinates_to_function(function_as_coordinates: List[Coordinate]) -> callable:
    elements_to_add = []
    for coordinate in function_as_coordinates:
        coefficient = coordinate.coefficient
        if coefficient == Dyadic(0):
            continue

        powers = coordinate.powers
        if coefficient in [-ONE, ONE]:
            elements_to_multiply = []
        else:
            elements_to_multiply = [f"Dyadic('{coefficient}')"]
        for i, power in enumerate(powers):
            if power == 0:
                continue

            x_i = f"x[{i}]"
            if power == 1:
                term = x_i
            else:
                term = f"pow({x_i},{power})"

            term = "-" + term if coefficient == -1 else term

            elements_to_multiply.append(term)

        if not elements_to_multiply:
            elements_to_multiply = [f"Dyadic('{coefficient}')"]

        elements_to_add.append("*".join(elements_to_multiply))

    function_as_string = "+".join(elements_to_add)
    function_as_string = "lambda x: " + function_as_string
    function = eval(function_as_string)

    return function
