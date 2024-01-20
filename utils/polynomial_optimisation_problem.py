from typing import List

from pyariadne import FloatDPExactBox
from pyariadne import ValidatedVectorMultivariateFunction


class PolynomialOptimisationProblem:
    f: ValidatedVectorMultivariateFunction
    D: FloatDPExactBox
    is_conversion_needed_per_dimension: List[bool]

    def __init__(
        self,
        f: ValidatedVectorMultivariateFunction,
        D: FloatDPExactBox,
        is_conversion_needed_per_dimension: List[bool]
    ) -> None:
        self.f = f
        self.D = D
        self.is_conversion_needed_per_dimension = is_conversion_needed_per_dimension
