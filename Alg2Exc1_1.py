import re

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

def parseImdb(dataset):
	mode = -1
	actors = []
	directors = []
	directors_genres = []
	movies = []
	movies_directors = []
	movies_genres = []
	roles = []
	with open("imdb-r.txt") as fd:
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
						movies.append((moviesMatch.group(1), moviesMatch.group(2), moviesMatch.group(3), moviesMatch.group(4), moviesMatch.group(5)))
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
				
	if dataset == 'actors':
		return actors
	if dataset == 'directors':
		return directors
	if dataset == 'directors_genres':
		return directors_genres
	if dataset == 'movies':
		return movies
	if dataset == 'movies_directors':
		return movies_directors
	if dataset == 'movies_genres':
		return movies_genres
	if dataset == 'roles':
		return roles
	#print(actors)
	# print(directors)
	# print(directors_genres)
	#print(movies)
	#print(movies_directors)
	# print(movies_genres)
	#print(roles)