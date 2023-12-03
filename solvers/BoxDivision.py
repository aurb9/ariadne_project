##EXAMPLE FILE IN PROGRESS OF GETTING A BOX DIVISION BY 1/BOX

from pyariadne import BoxDomainType, FloatDP, dp



INF = FloatDP.inf(dp)
#B=BoxDomainType([("0.5", INF)]) #case 1
#B=BoxDomainType([("-0.5", INF)]) #case 2
B = BoxDomainType([(-INF, "-0.5")]) #case 3

print('Original box', B)


l = B[0].lower_bound()
u = B[0].upper_bound()


#if LOWER_BOUND > 0:
#   Therefore, the UPPER_BOUND > 0, so:
#      LOWER_BOUND --> NEW_UPPER_BOUND
#      AND
#      UPPER_BOUND --> NEW_LOWER_BOUND
if l > ZERO and u > ZERO:
    # if l > FloatDP(0, dp): #can be converted later, but since u<l we need this check
    print('Case 1')
    NEW_l = ONE/u
    NEW_u = ONE/l
    #print(type(NEW_u.lower())) #get lowerbound type
    #print(NEW_u.lower()) #get lowebound
    #print(NEW_u.lower().raw()) #get float data of lb
    #print(type(NEW_u.lower().raw())) #FloatDP
    NEW_u = NEW_u.lower().raw()
    NEW_l = NEW_l.lower().raw()

    #print(NEW_u)
    #print(NEW_l)
    B_prime = BoxDomainType([(NEW_l, NEW_u)])
    print('New box:', B_prime)
elif l < ZERO < u:
    print('Case 2')
    #E.g. [-1, 2] --> 1/-1, 1/2 --> -1, 1/2 --> [-1, 1/2]
    #E.g. [-10, 5] --> 1/-10, 1/5 --> -1/10, 1/5
    #Since l<0, 1/l stays negative
    #Since u>0, 1/u stays positive
    NEW_l = ONE/l
    NEW_u = ONE/u

    NEW_u = NEW_u.lower().raw()
    NEW_l = NEW_l.lower().raw()

    B_prime = BoxDomainType([(NEW_l, NEW_u)])
    print('New box:', B_prime)
elif l < ZERO and u < ZERO:
    print('Case 3')
    #E.g. [-10, -2] --> -1/10, -1/2 so l and u get swapped

    NEW_l = ONE/u
    NEW_u = ONE/l

    NEW_u = NEW_u.lower().raw()
    NEW_l = NEW_l.lower().raw()

    B_prime = BoxDomainType([(NEW_l, NEW_u)])
    print('New box:', B_prime)
else:
    print('Not identified case, please resolve')