from typing import List
from typing import Tuple

from pyariadne import BoxDomainType
from pyariadne import dp
from pyariadne import FloatDP
from pyariadne import FloatDPPoint
from pyariadne import Function
from pyariadne import ValidatedFeasibilityProblem
from pyariadne import ValidatedKleenean
from pyariadne import ValidatedNumberVector


def split_box_around_zero(box: BoxDomainType) -> Tuple[BoxDomainType, BoxDomainType]:
    # TODO: or use split(around=0)?
    boxes = (
        BoxDomainType([(box[0].lower_bound(), FloatDP(0, dp))]),
        BoxDomainType([(FloatDP(0, dp), box[0].upper_bound())])
    )
    return boxes


def _convert_polynomial(p: ValidatedFeasibilityProblem) -> List[ValidatedFeasibilityProblem]:
    div = Function(1, lambda x: x)
    g = p.g[0] / div[0]  # TODO: convert function to 1/x ==> look at the bottom
    domain = p.D  # TODO: convert domain also to be 1/D
    zero = FloatDP(0, dp)
    # TODO: use zero instead?
    if domain.contains(FloatDPPoint(1, dp)):
        domain_left, domain_right = split_box_around_zero(box=domain)
        problems = [
            ValidatedFeasibilityProblem(domain_left, g, p.C),
            ValidatedFeasibilityProblem(domain_right, g, p.C)
        ]
    else:
        problems = [ValidatedFeasibilityProblem(p.D, g, p.C)]

    return problems


class PolynomialOptimiser:  # (ValidatedOptimiserInterface):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def _feasible_problem(self, p: ValidatedFeasibilityProblem) -> ValidatedKleenean:
        # TODO: implement

        return ValidatedKleenean(False)

    # TODO: should be either feasible point
    #  or "certificate of feasibility" (collection of pairs of boxes and multipliers)
    def feasible(self, p: ValidatedFeasibilityProblem) -> ValidatedKleenean:
        problems = _convert_polynomial(p=p)
        for problem in problems:
            if self._feasible_problem(p=problem) == "false":  # TODO: can be changed to not self._feasible?
                return ValidatedKleenean(False)

        return ValidatedKleenean(True)

    def minimise(self, p: ValidatedFeasibilityProblem) -> ValidatedNumberVector:
        problems = _convert_polynomial(p=p)
        # opt = nul(...)
        for problem in problems:
            pass # TODO: solve each and return lowest value
        # TODO: set gradient to 0 and use Newton approach
        pass


opt = PolynomialOptimiser()
g = Function(1, lambda x: x)  # when we define this, we get an EffectiveMultivariateFunction, how to
# get x out of this for instance (i.e., the function)

# p(x) = a_0 + a_1*x + ...
# q(x) = x^2 * p / x

# ==> either dict or use expression from ariadne
# then use RealValuation


# Make polynomial class / function that returns list of index and coefficients ==> parse that back
# to polynomial ariadne function
C = BoxDomainType([{"-0.0625": "0.0625"}])
D1 = BoxDomainType([(-1, FloatDP.inf(dp))])
fp1 = ValidatedFeasibilityProblem(D1, g, C)
print(opt.feasible(fp1))
