from pyariadne import *

opt = InteriorPointOptimiser()

# Define the initial condition and time horizon
initial_condition = 9

# Euler setup 
# h = 0.1
n = 2

v=FloatDPBounds({"-5":"-4"},dp)
D= BoxDomainType([{-5:-3}])
g = Function(1, lambda v :v)

def euler_update_x(x):
    # x = exact(-34)
    return Function(1, lambda v:   x + ((-pow(x,2) + v[0] )/n))

for i in range(0,n):
    if i == 0 :
        x_new = euler_update_x(initial_condition)
        print(x_new)
    else:
        # -----------------------
        # TRYED TO DO THIS BUT THEN HAVING PROBLEM WITH (-pow(x,2) + v[0]
        # print(o)
        x = evaluate(x_new ,ExactDouble(o))
        print(x)
        # print(type(exact(x)))
        # -----------------------
        # x = x_new
        x_new = euler_update_x(x)
        print(x_new)

    p = ApproximateOptimisationProblem(-pow(x_new,2),D,g,D)
    print("p:",p) 
    o = opt.minimise(p)
    print('v values: ',o)
    obejective_value = evaluate(-pow(x_new,2),FloatDPApproximationVector(o, dp) )
    print('objective value', obejective_value)
