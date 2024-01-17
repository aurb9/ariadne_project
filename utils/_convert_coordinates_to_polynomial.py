from typing import List

from pyariadne import dp
from pyariadne import FloatDPBounds
from pyariadne import MultivariatePolynomial

from utils._coordinate import Coordinate


def convert_coordinates_to_polynomial(function_as_coordinates: List[Coordinate]) -> MultivariatePolynomial:
    polynomial_as_coordinates = {
        x.powers: x.coefficient for x in function_as_coordinates
    }
    polynomial = MultivariatePolynomial[FloatDPBounds](polynomial_as_coordinates, dp)

    return polynomial
