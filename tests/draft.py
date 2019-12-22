import random

l = list(set([1, 2, 3] + [1, 2, 4]))
print(l)
random.shuffle(l)
print(l)
n = random.randint(1, 3)
print(n)
print(l[:n])
