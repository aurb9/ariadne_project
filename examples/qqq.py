import re
from utils._coordinate import Coordinate



def evaluate_expression(expression):
    stack = []
    current_operand = None

    for token in expression:
        if token == '(':
            if current_operand is not None:
                stack.append(current_operand)
            current_operand = None
        elif token == ')':
            if current_operand is not None:
                stack.append(current_operand)
            current_operand = None
            while len(stack) > 1 and stack[-2] != '(':
                operand2 = stack.pop()
                operand1 = stack.pop()
                result = operand1 * operand2
                stack.append(result)
            stack.pop()
        elif token == '*':
            continue
        else:
            current_operand = token

    if current_operand is not None:
        stack.append(current_operand)

    print(stack)
    input()

    # Process any remaining operations on the stack
    while len(stack) > 1:
        operand2 = stack.pop()
        operator = stack.pop()
        operand1 = stack.pop()
        result = operand1 * operand2
        stack.append(result)

    return stack[0]

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

result = evaluate_expression(res)
print(result)