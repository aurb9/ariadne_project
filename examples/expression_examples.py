from pyariadne import Variable, Real, Constant, dy_
from pyariadne import derivative, simplify, make_function


### FIRST PART - Create an expression and differentiate it.

print('FIRST PART')

# SETUP:
x = Variable[Real]("x")
c = Constant[Real]("c", dy_(3.75))  # Dyadic

# Formulation 1:
e_1 = c * x * x
print('First formulation:')
print(e_1)
diff_e = derivative(e_1, x)  # Take derivative w.r.t. x
print(diff_e)
print('Simplify:', simplify(diff_e))
print()


# ALTERNATIVE FORMULATION:
e_1 = c * x**2  # is automatically converted to pow(x,2)
# e_1 = c * pow(x,2) # Need to import pow

print('Alternative formulation:')
print(e_1)
diff_e = derivative(e_1, x)  # Take derivative w.r.t. x
print(diff_e)
print('Simplify:', simplify(diff_e))




### SECOND PART - combining expressions
print("="*100)
print('SECOND PART')

# Let's try to ADD 3.75*x^3 to the old expression
e_2 = c * x**3
e_combined = e_1 + e_2
print(e_combined)

# Let's try to MULTIPLY 3.75*x^3 to the old expression
e_2 = c * x**3
e_combined = e_1 * e_2
print(e_combined)

# We can also put new variables in
y = Variable[Real]("y")
e_2 = c * y**3
e_combined = e_1 + e_2
print(simplify(e_combined))


### THIRD PART - making functions from expressions
print("="*100)
print('THIRD PART')

print(make_function(x, e_1))

