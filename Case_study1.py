#!/usr/bin/python3

# nonlinear_programming_demonstration.py
# Copyright  2023  Pieter Collins
#
# This file is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This file is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTAXILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this file. If not, see <https://www.gnu.org/licenses/>.



# difference between C and D 
#  different between , : "" {} []
# what is InfeasibleInteriorPointOptimiser 


from pyariadne import *

def tanh(x):
    return (exp(x) - exp(-x)) / (exp(x) + exp(-x))

# def atanh(x):
#     if abs(x) > 1:
#         raise ValueError("Input must be in the range (-1, 1)")
#     return 0.5 * log((1 + x) / (1 - x))

opt = InteriorPointOptimiser()


v1=FloatDPBounds({"0":"5"},dp)
print("v1:",v1)
v2=FloatDPBounds({"-5":"0"},dp)
print("v2:",v2)

g = Function(1, lambda v :v)
# print("g", g)


f1 = Function (1, lambda v1 : -pow  ((sqrt(v1[0]) * ((sqrt(v1[0])*tanh(sqrt(v1[0])) + 9) )   / ((sqrt(v1[0])+tanh(sqrt(v1[0])) *9))   ),2))
print("f1",f1)

# --------------------  THESE PRINTS ARE FOR TESTING ----------------
# print(sqrt(-v2))
# print(tan(sqrt(-v2)))
# print(tan(sqrt(-v2))*9)
# print(sqrt(-v2)*tan(sqrt(-v2)))
# print(sqrt(-v2)*tan(sqrt(-v2))-9)
# print(sqrt(-v2) +tan(sqrt(-v2))*9)
# print(((-v2*tan(sqrt(-v2))) - (9* sqrt(-v2)) )  )
# print(sqrt(-v2)*(sqrt(-v2)*tan(sqrt(-v2))-9))
# print((sqrt(-v2)*tan(sqrt(-v2)) - 9) )
# print(tan(sqrt(-v2)))
# print((sqrt(-v2)+tan(sqrt(-v2))*9)  )
# # print(-pow  ((  sqrt(-v2) * ((sqrt(-v2)*tan(sqrt(-v2)) - 9) )   / ((sqrt(-v2)+tan(sqrt(-v2)) *9))   ),2))
# # print( mul( sqrt(-v2) , ((sqrt(-v2)*tan(sqrt(-v2)) - 9) )   / ((sqrt(-v2)+tan(sqrt(-v2)) *9)) ))
# print( ( sqrt(-v2) * (sqrt(-v2)*tan(sqrt(-v2)) - 9)) /(sqrt(-v2)+tan(sqrt(-v2)) *9)  )  # -26.544
# print( -pow(( sqrt(-v2) * (sqrt(-v2)*tan(sqrt(-v2)) - 9)) /(sqrt(-v2)+tan(sqrt(-v2)) *9),2)  )  # -26.544
# print(-v2*tan(sqrt(-v2)))https://www.gstatic.com/education/formulas2/553212783/en/eulers_formula.svg
# print(-v2*tan(sqrt(-v2)))

# print((9* sqrt(-v2))) 


# f2 with initial condition 
# f2 = Function (1, lambda v2 : -pow  ((  sqrt(-v2[0]) * ((sqrt(-v2[0])*tan(sqrt(-v2[0])) - 9) )   / ((sqrt(-v2[0])+tan(sqrt(-v2[0])) *9))   ),2))
f2 = Function (1, lambda v2 : -pow  ((   (-v2[0]*tan(sqrt(-v2[0])) - (9* sqrt(-v2[0])) )   / ((sqrt(-v2[0])+tan(sqrt(-v2[0])) *9))   ),2))


# f2 without initial condition 
# f2 = Function (1, lambda v2 : - pow((sqrt(-v2[0]) * tan(-sqrt(-v2[0]))),2))
print("f2",f2)

D1=BoxDomainType([{0:5}])
D2=BoxDomainType([{-5:0}])


C1=BoxDomainType([{0:5}])
C2=BoxDomainType([{-5:5}])


p1 = ApproximateOptimisationProblem(f1,D1,g,C1)
print("p1:",p1) 

p2 = ApproximateOptimisationProblem(f2,D2,g,C2)
print("p2:",p2) 

o = [opt.minimise(p1), opt.minimise(p2)]
print('v values: ',o)

print(evaluate(f1,FloatDPApproximationVector(o[0], dp) ))
print(evaluate(f2,FloatDPApproximationVector(o[1], dp) ))

obejective_value = min(evaluate(f1,FloatDPApproximationVector(o[0], dp) ), evaluate(f2,FloatDPApproximationVector(o[1], dp) ))

print("objective value: ",obejective_value)
