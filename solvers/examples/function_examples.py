from pyariadne import Function, pow

f = Function(1, lambda x: [pow(x[0], 2)])
print(f)
f_der = f.derivative(0)  # 0 indicates w.r.t. the 0th variable, so x[0]
print(f_der)
