import numpy as np

xs = [(1, 2, 3), (3, 4, 5)]

xs = np.transpose(xs)

print(xs.mean(1))
