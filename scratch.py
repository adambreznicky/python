__file__ = 'scratch'
__date__ = '3/6/2015'
__author__ = 'ABREZNIC'
from decimal import *
joe = 5.2238884512861
print joe

string = str(joe)
print string
num = string.split(".")[0]
dec = string.split(".")[1]
keep = dec[:3]
new = num + "." + keep
print new

number = float(new)
print number
multi = number * 2
print multi

# frmt = format(joe, '.3f')
# print frmt
# frmt2 = Decimal(frmt)
# print frmt2
# output = frmt2 * 2
# print output

# getcontext().prec = 3
# getcontext.rounding = ROUND_UP
# output = Decimal(joe)
# print output


