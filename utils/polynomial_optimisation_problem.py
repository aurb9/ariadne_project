from typing import List

from pyariadne import FloatDPExactBox
from pyariadne import ValidatedVectorMultivariateFunction


class PolynomialOptimisationProblem:
    f: ValidatedVectorMultivariateFunction
    D: FloatDPExactBox
    domains: List[bool]

    def __init__(self, f: ValidatedVectorMultivariateFunction, D: FloatDPExactBox, domains: List[bool]):
        self.f = f
        self.D = D
        self.domains = domains
