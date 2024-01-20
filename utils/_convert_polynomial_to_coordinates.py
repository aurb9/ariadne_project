from typing import List

from pyariadne import MultivariatePolynomial

from utils._coordinate import Coordinate


def convert_polynomial_to_coordinates(f: MultivariatePolynomial) -> List[Coordinate]:
    coordinates = [Coordinate(coefficient=x.coefficient(), powers=x.index()) for x in f]

    return coordinates
