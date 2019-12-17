import os

l = [1, 2, 3]
a = [4,5,6]
print([(i, j) for i, j in zip(reversed(l), reversed(a))])
