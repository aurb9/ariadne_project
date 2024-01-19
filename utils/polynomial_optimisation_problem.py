from typing import Tuple

from pyariadne import FloatDPExactBox
from pyariadne import ValidatedVectorMultivariateFunction


class PolynomialOptimisationProblem:
    f: ValidatedVectorMultivariateFunction
    D: FloatDPExactBox
    domains: Tuple[str]

    def __init__(self, f: ValidatedVectorMultivariateFunction, D: FloatDPExactBox, domains: Tuple[str]):
        self.f = f
        self.D = D
        self.domains = domains
