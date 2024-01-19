from typing import Any
from typing import List
from typing import Optional

from pyariadne import derivative
from pyariadne import dp
from pyariadne import evaluate
from pyariadne import FloatDP
from pyariadne import FloatDPBounds
from pyariadne import FloatDPBoundsVector
from pyariadne import MultiIndex
from pyariadne import MultivariatePolynomial
from pyariadne import Rational
from pyariadne import ValidatedScalarMultivariateFunction

from utils._convert_coordinates_to_function import convert_coordinates_to_function
from utils._convert_coordinates_to_polynomial import convert_coordinates_to_polynomial
from utils._convert_polynomial_to_coordinates import convert_polynomial_to_coordinates
from utils._coordinate import Coordinate
from utils._scalar import is_scalar

_OPERATION_NOT_POSSIBLE_ERROR_MESSAGE = f"Operation not possible for objects of type PolynomialFunction and "


class PolynomialFunction:
    _n_variables: int
    _coordinates: List[Coordinate]

    def __init__(
        self,
        n_variables: int,
        f: Optional[MultivariatePolynomial] = None,
        coordinates: Optional[List[Coordinate]] = None
    ) -> None:
        assert f or coordinates, "Need to specify either the function or the coordinates"
        self._n_variables = n_variables
        if f:
            self._coordinates = convert_polynomial_to_coordinates(f=f)
        else:
            self._coordinates = coordinates
        if f and coordinates:
            assert convert_polynomial_to_coordinates(f=f) == coordinates

    def __repr__(self) -> str:
        return str(self.function)

    def __call__(self, x: Any) -> Any:
        if is_scalar(x=x) or isinstance(x, FloatDP):
            x_to_evaluate = FloatDPBoundsVector([x], dp)
        elif isinstance(x, FloatDPBounds) or isinstance(x, FloatDPBoundsVector):
            x_to_evaluate = x
        else:
            raise Exception(f"PolynomialFunction object is not callable with object of type {type(x)}")

        result = evaluate(self.polynomial, x_to_evaluate)

        return result

    # TODO: all operations should be used from MultivariatePolynomial
    def __neg__(self) -> "PolynomialFunction":
        coordinates = [-x for x in self._coordinates]
        result = PolynomialFunction(n_variables=self._n_variables, coordinates=coordinates)

        return result

    def __add__(self, other: Any) -> "PolynomialFunction":
        coordinates = self._coordinates.copy()
        if is_scalar(x=other):
            constant_coordinate = MultiIndex([0 for _ in range(self._n_variables)])
            other_coordinate = Coordinate(coefficient=FloatDPBounds(str(other), dp), powers=constant_coordinate)
            did_update = False
            for i, x in enumerate(coordinates):
                if x.powers == constant_coordinate:
                    coordinates[i] = x + other_coordinate
                    did_update = True
                    break
            if not did_update:
                coordinates.append(other_coordinate)
        elif isinstance(other, PolynomialFunction):
            other_coordinates = other._coordinates
            for y in other_coordinates:
                did_update = False
                for i, x in enumerate(coordinates):
                    if x.powers == y.powers:
                        coordinates[i] = x + y
                        did_update = True
                        break
                if not did_update:
                    coordinates.append(y)
        else:
            raise Exception(_OPERATION_NOT_POSSIBLE_ERROR_MESSAGE, type(other))

        result = PolynomialFunction(n_variables=max(self._n_variables, other.n_variables), coordinates=coordinates)

        return result

    def __radd__(self, other: Any) -> "PolynomialFunction":
        return self.__add__(other=other)

    def __sub__(self, other: Any) -> "PolynomialFunction":
        return self.__add__(other=-other)

    def __mul__(self, other: Any) -> "PolynomialFunction":
        if is_scalar(x=other):
            coordinates = [x*other for x in self._coordinates]
            n_variables = self._n_variables
        elif isinstance(other, PolynomialFunction):
            coordinates = [x*y for x in self._coordinates for y in other._coordinates]
            n_variables = max(self._n_variables, other._n_variables)
        else:
            raise Exception(_OPERATION_NOT_POSSIBLE_ERROR_MESSAGE, type(other))

        result = PolynomialFunction(n_variables=n_variables, coordinates=coordinates)

        return result

    def __rmul__(self, other: Any) -> "PolynomialFunction":
        return self.__mul__(other=other)

    def _reciprocal(self) -> "PolynomialFunction":
        coordinates = [1/x for x in self._coordinates]
        result = PolynomialFunction(n_variables=self._n_variables, coordinates=coordinates)

        return result

    def __truediv__(self, other: Any) -> "PolynomialFunction":
        if is_scalar(x=other):
            other_reciprocal = FloatDPBounds(Rational(1, other))
        elif isinstance(other, PolynomialFunction):
            other_reciprocal = other._reciprocal()
        else:
            raise Exception(_OPERATION_NOT_POSSIBLE_ERROR_MESSAGE, type(other))

        result = self.__mul__(other=other_reciprocal)
        return result

    def __rtruediv__(self, other: Any) -> "PolynomialFunction":
        if not is_scalar(x=other):
            raise Exception(_OPERATION_NOT_POSSIBLE_ERROR_MESSAGE, type(other))

        self_reciprocal = self._reciprocal()
        result = self_reciprocal.__mul__(other=other)
        return result

    def derivative(self, n: int) -> "PolynomialFunction":
        derivative_polynomial = derivative(self.polynomial, n)
        result = PolynomialFunction(n_variables=self.n_variables, f=derivative_polynomial)

        return result

    def second_derivative(self, n_1: int, n_2: Optional[int] = None) -> "PolynomialFunction":
        first_derivative = self.derivative(n_1)
        if n_2 is None: n_2 = n_1
        second_derivative = first_derivative.derivative(n_2)

        return second_derivative

    # TODO: eventually this should go to __call__
    def evaluate_at_one_over_x(self, n: int) -> "PolynomialFunction":
        coordinates = [x.one_over_x(n=n) for x in self._coordinates]
        result = PolynomialFunction(n_variables=self._n_variables, coordinates=coordinates)

        return result

    @property
    def n_variables(self) -> int:
        return self._n_variables

    @property
    def polynomial(self) -> MultivariatePolynomial:
        f_as_polynomial = convert_coordinates_to_polynomial(coordinates=self._coordinates)

        return f_as_polynomial

    @property
    def function(self) -> ValidatedScalarMultivariateFunction:
        f = convert_coordinates_to_function(n_variables=self._n_variables, coordinates=self._coordinates)
        return f

    def max_degree_nth_variable(self, n: int) -> int:
        assert n < self._n_variables, f"{n}th variable does not exist, there are at most {self._n_variables} variables"

        max_degree = max([x.powers[n] for x in self._coordinates])
        return max_degree

    @staticmethod
    def coordinate(n: int, i: int) -> "PolynomialFunction":
        powers = [0 for _ in range(n)]
        powers[n] = i
        coefficient = FloatDPBounds("1", dp)
        coordinates = [Coordinate(coefficient=coefficient, powers=MultiIndex(powers))]
        result = PolynomialFunction(n_variables=n, coordinates=coordinates)

        return result

    @staticmethod
    def constant(c: Any) -> "PolynomialFunction":
        coordinates = [Coordinate(coefficient=FloatDPBounds(str(c), dp))]

        return PolynomialFunction(n_variables=0, coordinates=coordinates)
