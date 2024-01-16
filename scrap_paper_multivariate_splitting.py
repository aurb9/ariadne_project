from itertools import product
from pyariadne import FloatDP, dp, FloatDPExactBox

from utils.polynomial_function import PolynomialFunction

INF = FloatDP.inf(dp)

b1 = (-INF, -1)
b2 = (-1, 1)
b3 = (1, INF)

domains_dict = {"b1": b1, "b2": b2, "b3": b3}
domains = ["b1", "b2", "b3"]

f = PolynomialFunction(n_variables=2, f="2*x[0]**2 + x[1]**2")
total_dimensions = f.n_variables

l_f = []
for dimension in range(total_dimensions):
    f_derivative = PolynomialFunction(n_variables=f.n_variables, f=f.function.derivative(dimension))

    max_degree = f.max_degree_nth_variable(n=dimension) - 1
    x_power_degree = PolynomialFunction(n_variables=f.n_variables, f=f"x[{dimension}]**{max_degree}")
    #print('x power degree: ', x_power_degree) #correct
    #print('f\'(1/x)', f_derivative.evaluate_at_one_over_x())
    q = x_power_degree.function * f_derivative.evaluate_at_one_over_x().function
    l_f.append([f_derivative, q])
#print(l_f)

l_d = list(product(domains, repeat=total_dimensions))
#print(l_d)

all_boxes = []
all_functions = []
for combination in l_d:
    subdomain_strings = [comb_part for comb_part in combination]
    subdomain_boxes = [domains_dict[comb_part] for comb_part in subdomain_strings]
    #print(subdomain_strings)

    functions = []
    for dim in range(len(l_f)):
        if subdomain_strings[dim] == 'b1' or subdomain_strings[dim] == 'b3':
            functions.append(l_f[dim][1])
        else:
            functions.append(l_f[dim][0])
    all_functions.append((functions))
    #print(subdomain_boxes)
    # print(subdomain.__contains__(b1) or subdomain.__contains__(b3))
    box = FloatDPExactBox(subdomain_boxes)
    # print(box)
    all_boxes.append(box)
assert(len(all_boxes) == len(all_functions))

#print(all_boxes)
# all_boxes = boxes^total_dimensions = 3^2 = 9
# all_functions = all_boxes, but there are only total_dimensions*2 = 2*2 = 4 unique functions
#print("="*100)
#print(all_functions)

PRINTING = False
if PRINTING:
    for i in range(len(all_boxes)):
        print('Index:', i+1)
        print('Box:', all_boxes[i])
        print('Functions:', all_functions[i])
        print()
