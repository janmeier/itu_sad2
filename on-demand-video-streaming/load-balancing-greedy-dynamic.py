import re
import datetime, time
#									Table name
lockExpr = re.compile("LOCK TABLES `(.*)`.*")
#						  Id      Firstname Lastname  Gender  Number of films
actorsExpr = re.compile(" (\d*),\'(\w*)\',\'(\w*)\',\'(\w*)\',(\d*).*")
#						     Id     Firstname Lastname
directorsExpr = re.compile(" (\d*),\'(\w*)\',\'(\w*)\'.*")
#						            Id(dir) Genres
directors_genresExpr = re.compile(" (\d*),\'(\w*)\'.*")
#						  Id      Title   Year  Rank  Minutes
moviesExpr = re.compile(" (\d*),\'(\w*)\',(\d*),(\w*),(\d*).*")
#						 			Id(mov) Id(dir)
movies_directorsExpr = re.compile(" (\d*),(\d*).*")
#						 		 Id     Genre
movies_genresExpr = re.compile(" (\d*),\'(\w*)\'.*")
#						 Id(act) Id(mov) Name
rolesExpr = re.compile(" (\d*),(\d*),\'(\w*)\'.*")

def parseImdb():
	mode = -1
	actors = []
	directors = []
	directors_genres = []
	movies = []
	movies_directors = []
	movies_genres = []
	roles = []
	with open("imdb-r.txt", encoding="utf8") as fd:
		for line in fd:
			lockMatch = lockExpr.match(line)
			if lockMatch:
				if(lockMatch.group(1) == "actors"):
					mode = 0
				elif(lockMatch.group(1) == "directors"):
					mode = 1
				elif(lockMatch.group(1) == "directors_genres"):
					mode = 2
				elif(lockMatch.group(1) == "movies"):
					mode = 3
				elif(lockMatch.group(1) == "movies_directors"):
					mode = 4
				elif(lockMatch.group(1) == "movies_genres"):
					mode = 5
				elif(lockMatch.group(1) == "roles"):
					mode = 6
			else:
				if(mode == 0):	#Actors
					actorsMatch = actorsExpr.match(line)
					if actorsMatch:
						actors.append((actorsMatch.group(1), actorsMatch.group(2), actorsMatch.group(3), actorsMatch.group(4), actorsMatch.group(5)))
				if(mode == 1):	#Directors
					directorsMatch = directorsExpr.match(line)
					if directorsMatch:
						directors.append((directorsMatch.group(1), directorsMatch.group(2), directorsMatch.group(3)))
				if(mode == 2):	#Director_genres
					directors_genresMatch = directors_genresExpr.match(line)
					if directors_genresMatch:
						directors_genres.append((directors_genresMatch.group(1), directors_genresMatch.group(2)))
				if(mode == 3):	#Movies
					moviesMatch = moviesExpr.match(line)
					if moviesMatch:
						rank = 0 if (moviesMatch.group(4) == "NULL") else int(moviesMatch.group(4))
						movies.append((moviesMatch.group(1), moviesMatch.group(2), moviesMatch.group(3), rank, int(moviesMatch.group(5))))
				if(mode == 4):	#Movies_directors
					movies_directorsMatch = movies_directorsExpr.match(line)
					if movies_directorsMatch:
						movies_directors.append((movies_directorsMatch.group(1), movies_directorsMatch.group(2)))
				if(mode == 5):	#Movies_genres
					movies_genresMatch = movies_genresExpr.match(line)
					if movies_genresMatch:
						movies_genres.append((movies_genresMatch.group(1), movies_genresMatch.group(2)))
				if(mode == 6):	#Roles
					rolesMatch = rolesExpr.match(line)
					if rolesMatch:
						roles.append((rolesMatch.group(1), rolesMatch.group(2), rolesMatch.group(3)))
				
	return movies
	#print(actors)
	#print(directors)
	#print(directors_genres)
	#print(movies)
	#print(movies_directors)
	#print(movies_genres)
	#print(roles)

totalMiniutes = 998
movies = parseImdb()
movies = [m for m in movies if m[3] >= 9] #Rating greater than or equal to 9
numberOfMovies = len(movies)
cache = [[0 for x in range(numberOfMovies)] for x in range(totalMiniutes+1)] #Jeg skal cache i og W
path = [[0 for x in range(numberOfMovies)] for x in range(totalMiniutes+1)]

def greedy():
	W = totalMiniutes
	movies.sort(key=lambda tup: tup[4], reverse = True)
	result = []
	for m in movies:
		if(m[4] <= W):
			result.append(m)
			W -= m[4]
	print(totalMiniutes - W)
	print(result)

def printDynamic():
	i = numberOfMovies-1
	W = totalMiniutes
	result = []
	while(i >= 0):
		if(path[W][i] == 1):
			result.append(movies[i])
			W -= movies[i][4]
			i -= 1
		else:
			i -= 1
	print(result)

def dynamic():
	print(OPT(numberOfMovies-1, totalMiniutes))
	printDynamic()

def OPT(i, W):
	if(W == 0 or i < 0):
		return 0

	elif(cache[W][i] != 0):
		return cache[W][i]
	
	elif(movies[i][4] > W):
		path[W][i] = -1
		cache[W][i] = OPT(i - 1, W)
		return cache[W][i]
	
	else:
		take = movies[i][4] + OPT(i - 1, W-movies[i][4])
		dontTake = OPT(i - 1, W)
		if(take >= dontTake):
			cache[W][i] = take	
			path[W][i] = 1
		else:
			cache[W][i] = dontTake	
			path[W][i] = -1
		return cache[W][i]

print("Running greedy version")
time_begin = datetime.datetime.fromtimestamp(time.time())
greedy()
time_end = datetime.datetime.fromtimestamp(time.time())
print("Time elapsed: ", str(time_end - time_begin))
print("Running dynamic version")
time_begin = datetime.datetime.fromtimestamp(time.time())
dynamic()
time_end = datetime.datetime.fromtimestamp(time.time())
print("Time elapsed: ", str(time_end - time_begin))