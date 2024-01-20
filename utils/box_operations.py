from typing import Tuple

from pyariadne import dp
from pyariadne import FloatDP
from pyariadne import FloatDPExactInterval


ZERO = FloatDP(0, dp)
ONE = FloatDP(1, dp)


def box_reciprocal(box: FloatDPExactInterval) -> FloatDPExactInterval:
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

    result = FloatDPExactInterval((new_box_lower_bound, new_box_upper_bound))

    return result
