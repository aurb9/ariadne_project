# Example file to convert a string, such as "1/2" to a FloatDP

from pyariadne import FloatDP, dp

fraction_string = "1/2"
# fl = FloatDP(s, dp) #gives error, so we need another way to convert it
numerator, denominator = fraction_string.split("/")
print(numerator)
print(denominator)
first = FloatDP(numerator, dp)
second = FloatDP(denominator, dp)

together = first/second
together = together.value()  # An approximation to the actual value
print(together)
print(type(together))
