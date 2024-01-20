from typing import List

from pyariadne import dp
from pyariadne import FloatDPBounds
from pyariadne import MultivariatePolynomial

from utils._coordinate import Coordinate


def convert_coordinates_to_polynomial(coordinates: List[Coordinate]) -> MultivariatePolynomial:
    polynomial_as_coordinates = {
        x.powers: x.coefficient for x in coordinates
    }
    polynomial = MultivariatePolynomial[FloatDPBounds](polynomial_as_coordinates, dp)

    return polynomial
