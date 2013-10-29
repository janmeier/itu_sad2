import sys
import os
from collections import deque

sys.path.append(os.getcwd())
import Alg2Exc1_1

print 'Begin parsing'
movies = Alg2Exc1_1.parseImdb('movies')
movies = [movie for movie in movies if movie[3] != 'NULL' and float(movie[3]) >= 9.0]
W = 1001

# movies = [
# 	('5284', 'Abuse', '1996', 'NULL', '15'),
# 	('5235', 'Absturz', '1990', 'NULL', '17'), 
# 	('5238', 'Absurd', '1989', 'NULL', '18'), 
# 	('5266', 'Abuelitos', '1999', '6', '15')
# ]
# W = 31

w = 0
m = {}
n = len(movies)

m[0] = [0] * W

for j in range (0, n + 1):
	m[j] = [0] * (W + 1)

print 'Begin calculations'
for i in range(1, n + 1):
	for j in range(0, W + 1):
		weight = value = int(movies[i-1][4])

		if j >= weight:
			m[i][j] = max(m[i-1][j], m[i-1][j-weight] + value)
		else:
			m[i][j] = m[i-1][j]

print m[n][W]

def FindSolution(i, j, buff):
	used_weight = m[i][j]

	while (i > 0 and j > 0):
		movie = movies[i - 1]
		if (m[i-1][j] < used_weight and m[i-1][j - int(movie[4])] == m[i][j] - int(movie[4])):
			buff.append(movie)

			i = i - 1 
			j = j - int(movie[4])
		else:
			i = i - 1

buff = []
FindSolution(n, W, buff)
print buff

## Result: 1000
## Timing: 1m7.571s, 1m6.535s, 1m7.772s