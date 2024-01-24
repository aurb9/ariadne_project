from pyariadne import *

def tanh(x):
    return (exp(x) - exp(-x)) / (exp(x) + exp(-x))

opt = InteriorPointOptimiser()


v1=FloatDPBounds({"0":"5"},dp)
print("v1:",v1)
v2=FloatDPBounds({"-5":"0"},dp)
print("v2:",v2)

g = Function(1, lambda v :v)
# print("g", g)


f1 = Function (1, lambda v1 : -pow  ((sqrt(v1[0]) * ((sqrt(v1[0])*tanh(sqrt(v1[0])) + 9) )   / ((sqrt(v1[0])+tanh(sqrt(v1[0])) *9))   ),2))
print("f1",f1)

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