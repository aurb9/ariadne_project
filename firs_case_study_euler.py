from pyariadne import *

opt = InteriorPointOptimiser()
opt2 = KarushKuhnTuckerOptimiser()

# Define the initial condition and time horizon
initial_condition = 9

# Euler setup 
# h = 0.1
n = 20

v=FloatDPBounds({"-5":"5"},dp)
D= BoxDomainType([{-5:5}])
g = Function(1, lambda v :v)

def euler_update_x(x):
    return Function(1, lambda v:   x + ((-pow(x,2) + v[0] )/n))

for i in range(0,n):
    if i == 0 :
        x_new = euler_update_x(initial_condition)
        # print(x_new)
    else:
        # x = evaluate(x_new ,FloatDPApproximationVector(o, dp))
        # print(x)
        x = x_new
        x_new = euler_update_x(x)

    # p = ValidatedOptimisationProblem(-pow(x_new,2),D,g,D)
    p = ApproximateOptimisationProblem(-pow(x_new,2),D,g,D)
    o = opt.minimise(p)
    print('v values: ',o)
    obejective_value = evaluate(-pow(x_new,2),FloatDPApproximationVector(o, dp) )
    print('objective value', obejective_value)

