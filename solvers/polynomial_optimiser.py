from typing import List
from typing import Tuple

from pyariadne import FloatDPExactBox
from pyariadne import FloatDPPoint
from pyariadne import nul
from pyariadne import dp
from pyariadne import FloatDP
from pyariadne import FloatDPExactInterval
from pyariadne import ValidatedNumberVector

from utils.polynomial_function import PolynomialFunction


ZERO = FloatDP(0, dp)
ONE = FloatDP(1, dp)


def _convert_single_box(box: FloatDPExactInterval) -> Tuple[FloatDP, FloatDP]:
    """
    Convert a single box by 1/box. E.g., box=[-5, 10] --> new_box = [-1/5, 1/10]
    :param subdomain: an interval with a lowerbound and upperbound in the original domain
    :return: tuple of (new_lowerbound and new_upperbound) for the creation of a new box
    """
    box_lower_bound = box.lower_bound()
    box_upper_bound = box.upper_bound()
    if box_lower_bound > ZERO and box_upper_bound > ZERO:
        new_box_lower_bound = ONE / box_upper_bound
        new_box_upper_bound = ONE / box_lower_bound
    elif box_lower_bound < ZERO < box_upper_bound:
        new_box_lower_bound = ONE / box_lower_bound
        new_box_upper_bound = ONE / box_upper_bound
    else:
        new_box_lower_bound = ONE / box_upper_bound
        new_box_upper_bound = ONE / box_lower_bound

    new_box_lower_bound = new_box_lower_bound.lower().raw()
    new_box_upper_bound = new_box_upper_bound.lower().raw()

    return new_box_lower_bound, new_box_upper_bound


def _box_reciprocal(box: FloatDPExactBox) -> FloatDPExactBox:
    """
    Converting the entire domain to 1/domain by going over every subdomain and converting that
    :param box: a box containing the domain (can be single or multiple)
    :return: the new_domain which is 1/input_domain
    """
    sub_boxes = []
    for dim_i in range(box.dimension()):
        sub_boxes.append(_convert_single_box(box[dim_i]))

    new_box = FloatDPExactBox(sub_boxes)
    return new_box


def _convert_problem(f: PolynomialFunction, D: FloatDPExactBox) -> List[Tuple[PolynomialFunction, FloatDPExactBox]]:
    # TODO: unsure how to get q and the new domains ==> to be implemented
    x_power_degree = PolynomialFunction(n_variables=f.n_variables, f=f"[x[0]**{f.degree}]")
    q = x_power_degree * f.evaluate_at_one_over_x()

    domain_reciprocal = _box_reciprocal(box=D)
    if domain_reciprocal.contains(FloatDPPoint([ZERO])):
        domain_left, domain_right = domain_reciprocal.split(0, ZERO)
        problems = [(q, domain_left), (q, domain_right)]
    else:
        problems = [(q, domain_reciprocal)]

    return problems


class PolynomialOptimiser:  # (ValidatedOptimiserInterface):
    # def __init__(self, *args, **kwargs) -> None:
    #     super().__init__(*args, **kwargs)

    def _minimise_over_box(self, function: PolynomialFunction, domain: FloatDPExactBox) -> ValidatedNumberVector:
        # TODO: implement using Newton approach
        pass

    def minimise(self, f: PolynomialFunction, D: FloatDPExactBox) -> ValidatedNumberVector:
        problems = _convert_problem(f=f, D=D)
        opt = nul(0)
        for x in problems:
            f = x[0]
            domain = x[1]
            gradients = [f.function.derivative(x) for x in range(f.n_variables)]

        # TODO: solve each and return lowest value
        # TODO: set gradient to 0 and use Newton approach

        return opt


solver = PolynomialOptimiser()

f = PolynomialFunction(n_variables=1, f="[x[0]**2]")
domain = FloatDPExactBox([(-1, FloatDP.inf(dp))])

opt = solver.minimise(f=f, D=domain)
print(opt)
