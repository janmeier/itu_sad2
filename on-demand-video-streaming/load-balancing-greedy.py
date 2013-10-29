import sys
import os

sys.path.append(os.getcwd())
import Alg2Exc1_1

print 'Begin parsing'
movies = Alg2Exc1_1.parseImdb('movies')
movies = [movie for movie in movies if movie[3] != 'NULL' and float(movie[3]) >= 9.0]

# movies = [
# 	('5235', 'Absturz', '1990', 'NULL', '173'), 
# 	('5238', 'Absurd', '1989', 'NULL', '179'), 
# 	('5266', 'Abuelitos', '1999', '6', '150'), 
# 	('5284', 'Abuse', '1996', 'NULL', '150')
# ]
# W = 300

print 'Begin sorting'

movies = sorted(movies, key=lambda movie: int(movie[4]))
used_movies = []

W = 1001
w = 0

print 'Begin calculations'

while (w < W and len(movies) > 0):
	movie = movies.pop()
	length = int(movie[4])

	if (w + length <= W):
		w = w + length
		used_movies.append(movie)

print used_movies
print w

## Result: 1000
## [
#	('378292', 'slovashaza', '1994', 'NULL', '179'), 
#	('377968', 'tude', '1961', 'NULL', '179'), 
#	('375276', 'Zischke', '1986', 'NULL', '179'), 
#	('375228', 'Zinloos', '2004', 'NULL', '179'), 
#	('375184', 'Zimzum', '2001', 'NULL', '179'), 
#	('375062', 'Zielscheiben', '1984', 'NULL', '105')
## ]
## Timing: 0m13.248s, 0m13.050s, 0m13.321s