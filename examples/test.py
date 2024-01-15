import re

from utils._coordinate import Coordinate
from utils.polynomial_function import PolynomialFunction


strrrr = "x0*(x0*(x0+1))+pow(x0,2)"
split_result = re.split(r'(pow\([^)]+\)|[()+]|\*(?=\())', strrrr)
res = []
for x in split_result:
    if x in ["", "+"]:
        continue
    if x in ["*", "(", ")"]:
        res.append(x)
        continue
    coordinate = Coordinate(n_variables=1, expression=x)
    res.append(coordinate)

print(res)
input()

# split_result = re.split(r'((?:pow\([^)]+\))|[()])+', strrrr)

print(split_result)
input()


PolynomialFunction(n_variables=1, f="x[0]*(x[0]+1)")
