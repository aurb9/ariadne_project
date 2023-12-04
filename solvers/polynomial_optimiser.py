from typing import List
from typing import Tuple

from pyariadne import BoxDomainType
from pyariadne import nul
from pyariadne import dp
from pyariadne import FloatDP
from pyariadne import FloatDPPoint
from pyariadne import FloatDPExactInterval
from pyariadne import Function
from pyariadne import pow
from pyariadne import ValidatedFeasibilityProblem
from pyariadne import ValidatedKleenean
from pyariadne import ValidatedNumberVector


ZERO = FloatDP(0, dp)
ONE = FloatDP(1, dp)


def _convert_single_box(subdomain: FloatDPExactInterval) -> Tuple[FloatDP, FloatDP]:
    """
    Convert a single box by 1/box. E.g., box=[-5, 10] --> new_box = [-1/5, 1/10]
    :param subdomain: an interval with a lowerbound and upperbound in the original domain
    :return: tuple of (new_lowerbound and new_upperbound) for the creation of a new box
    """
    l = subdomain.lower_bound()
    u = subdomain.upper_bound()
    if l > ZERO and u > ZERO:
        l_new = ONE / u
        u_new = ONE / l
    elif l < ZERO < u:
        l_new = ONE / l
        u_new = ONE / u
    else:
        l_new = ONE / u
        u_new = ONE / l

    l_new = l_new.lower().raw()
    u_new = u_new.lower().raw()

    return l_new, u_new

def _convert_domains(domain: BoxDomainType) -> BoxDomainType:
    """
    Converting the entire domain to 1/domain by going over every subdomain and converting that
    :param domain: a box containing the domain (can be single or multiple)
    :return: the new_domain which is 1/input_domain
    """
    subdomains = []
    for dim_i in range(domain.dimension()):
        subdomains.append(_convert_single_box(domain[dim_i]))
    new_domain = BoxDomainType(subdomains)

    return new_domain


def _convert_polynomial(p: ValidatedFeasibilityProblem) -> List[ValidatedFeasibilityProblem]:
    div = Function(1, lambda x: x)
    g = _convert_function_to_TODO(function=p.g)
    original_domain = p.D
    domain = _convert_domains(original_domain)

    if domain.contains(FloatDPPoint([ZERO])):
        domain_left, domain_right = domain.split(0, ZERO)
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

    def _is_problem_feasible(self, p: ValidatedFeasibilityProblem) -> ValidatedKleenean:
        # TODO: implement

        return ValidatedKleenean(False)

    # TODO: should be either feasible point
    #  or "certificate of feasibility" (collection of pairs of boxes and multipliers)
    def feasible(self, p: ValidatedFeasibilityProblem) -> ValidatedKleenean:
        problems = _convert_polynomial(p=p)
        for problem in problems:
            if self._is_problem_feasible(p=problem) == "false":  # TODO: can be changed to not self._feasible?
                return ValidatedKleenean(False)

        return ValidatedKleenean(True)

    def _solve_problem(self, p: ValidatedFeasibilityProblem) -> ValidatedNumberVector:
        # TODO: implement using Newton approach
        pass

    def minimise(self, p: ValidatedFeasibilityProblem) -> ValidatedNumberVector:
        problems = _convert_polynomial(p=p)
        opt = nul(0)
        for problem in problems:
            pass
            # TODO: solve each and return lowest value
        # TODO: set gradient to 0 and use Newton approach

        return opt


solver = PolynomialOptimiser()
g = Function(2, lambda x: [pow(x[0], 2) + 3 * x[1] - 1])
#g = Function(1, lambda x: [pow(x[0], 2) + 3 * x[0] - 1]) #1D function
C = BoxDomainType([{"-0.0625": "0.0625"}])
D1 = BoxDomainType([(-1, FloatDP.inf(dp))])
fp1 = ValidatedFeasibilityProblem(D1, g, C)
print(solver.feasible(fp1))
