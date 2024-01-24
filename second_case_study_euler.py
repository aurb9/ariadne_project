from pyariadne import *

opt = InteriorPointOptimiser()
opt2 = KarushKuhnTuckerOptimiser()

# Define the initial condition and time horizon
x0 = [1,1]

# Euler setup 
# h = 0.1
n = 1

v=FloatDPBounds({"-1":"1"},dp)
D= BoxDomainType([{-2:2}])
g = Function(1, lambda v :v)

def euler_update_x(x):
    return [Function(1, lambda v:  ((x[0]*8) + (x[1]*2) + (v[0]*2)) /(n*10)),
            Function(1, lambda v:  ((x[0]*1) + (x[1]*9) + (v[0]*1)) /(n*10))]


for i in range(0,n):
    if i == 0 :
        x_new = euler_update_x(x0)
        # print(x_new)
    else:
        # x = evaluate(x_new ,FloatDPApproximationVector(o, dp))
        # print(x)
        x = x_new
        x_new = euler_update_x(x)
    
    d = Function(1, lambda v: pow(x_new[0],2) +pow(x_new[1],2)+ 3*pow(x0[0],2) + 4* x0[0]*x0[1]+ pow(x0[1],2) - pow(v[0],2))
    p = ApproximateOptimisationProblem(d,D,g,D)
    print("p:",p) 
    o = opt.minimise(p)
    print('v values: ',o)
    obejective_value = evaluate(d,FloatDPApproximationVector(o, dp) )
    print('objective value', obejective_value)
