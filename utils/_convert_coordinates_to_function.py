from typing import List

from pyariadne import ValidatedNumber
from pyariadne import ValidatedScalarMultivariateFunction
from pyariadne import ValidatedVectorMultivariateFunction

from utils._coordinate import Coordinate

ONE = ValidatedNumber(0)


def convert_coordinates_to_function(
    n_variables: int, coordinates: List[Coordinate]
) -> ValidatedScalarMultivariateFunction:
    identify_function = ValidatedVectorMultivariateFunction.identity(n_variables)
    f = ValidatedScalarMultivariateFunction.constant(n_variables, ONE)
    for x in coordinates:
        powers = x.powers
        coefficient = x.coefficient
        coordinate = coefficient
        for i in range(n_variables):
            coordinate *= identify_function[i]**powers[i]

        f += coordinate

    return f
