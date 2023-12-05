# EXAMPLE FILE IN PROGRESS OF GETTING A BOX DIVISION BY 1/BOX
from typing import Tuple
from pyariadne import BoxDomainType, FloatDP, dp, FloatDPExactInterval

ZERO = FloatDP(0, dp)
ONE = FloatDP(1, dp)
INF = FloatDP.inf(dp)


def _convert_single_box(subdomain: FloatDPExactInterval) -> Tuple[FloatDP, FloatDP]:
    """
    Convert a single box by 1/box. E.g., box=[-5, 10] --> new_box = [-1/5, 1/10]
    :param subdomain: an interval with a lowerbound and upperbound in the original domain
    :return: tuple of (new_lowerbound and new_upperbound) for the creation of a new box
    """
    lower_bound = subdomain.lower_bound()
    upper_bound = subdomain.upper_bound()
    if lower_bound > ZERO and upper_bound > ZERO:
        l_new = ONE / upper_bound
        u_new = ONE / lower_bound
    elif lower_bound < ZERO < upper_bound:
        l_new = ONE / lower_bound
        u_new = ONE / upper_bound
    else:
        l_new = ONE / upper_bound
        u_new = ONE / lower_bound
    l_new = l_new.value()
    u_new = u_new.value()

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


case1 = (-INF, "-5")  # unbounded domain, strictly negative
case2 = (-INF, "5")  # unbounded domain, containing zero
case3 = ("-5", INF)  # unbounded domain, containing zero
case4 = ("5", INF)  # unbounded domain, strictly positive
# case5 = (-INF, INF)  # unbounded domain, containing 0
B = BoxDomainType([case1, case2, case3, case4])
print('Original box', B)


B_prime = _convert_domains(domain=B)
print('New box:', B_prime)
