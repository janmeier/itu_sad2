import sys
import datetime, time
import random
import copy
from collections import deque

class Actor:
	def __init__(self, name, actorId):
		self.name = name
		self.id = self.actorId = actorId
		self.colleagues = {}
		self.contracted = [actorId]

	def __repr__(self):
		return self.actorId + " " + self.name

class Movie:
	def __init__(self, title, rating, actors):
		self.title = title
		self.rating = rating
		self.actors = actors

	def __repr__(self):
		return self.name

def parseImdb(max_depth = sys.maxint):
	graph = {}
	i = 0
	movie = None
	with open("imdbMovieActorLastTenYears.csv") as fd:
		lastMovieId = 0
		for line in fd:
			values = line[0:-1].split(';')
			movieTitle = values[0]
			movieId = values[1]
			actorName = values[4] + " " + values[5]
			actorId = values[6]
			actor = Actor(actorName, actorId)
			# Check if this movie is the same as for the last line
			if(movieId == lastMovieId):
				movie.actors.append(actor)
			else:
				if(i > 0):
					buildGraph(movie, graph)
				movie = Movie(movieTitle, movieId, [actor])
				lastMovieId = movieId
			i += 1	

			if i > max_depth:
				break
	return graph

def buildGraph(movie, graph):
	# Make sure all actors in this movie are added to the graph
	for actor in movie.actors:
		if(not actor.actorId in graph):
			graph[actor.actorId] = actor
	# Add edges between all actors
	for actor1 in movie.actors:
		for actor2 in movie.actors:
			if(actor1.actorId != actor2.actorId):
				# Add an edge bewteen them, 1 means one edge (used for contraction)
				graph[actor1.actorId].colleagues[actor2.actorId] = 1

def bfs(graph, root, debug):
	q = deque() # The queue of nodes to visit
	v = {} # Visited
	q.append(root)
	v[root] = 1
	while(len(q) > 0):
		actor1 = graph[q.popleft()]
		if(debug):
			print("Id: ", actor1.actorId)	
		for actor2Id in actor1.colleagues:
			if(not actor2Id in v):
				v[actor2Id] = 1
				q.append(actor2Id)
	return v

def findConnectedComponents(graph):
	graphSize = len(graph)
	nodes = {x: 1 for x in graph.keys()}
	#nodes = list(set(originalGraph.keys()))
	components = []
	found = 0
	while(found < graphSize):
		root = list(nodes)[0]
		debug = root == 96529
		visited = bfs(graph, root, debug)
		found += len(visited)
		components.append(list(visited))
		for node in visited:
			del nodes[node]
	return components

# !!! TO BE REIMPLEMENTED !!!
# The code underneath can be used to calculate global min cut

#runs = 7000
#time_begin = datetime.datetime.fromtimestamp(time.time())
#runContractMultipleTimes(newOriginalGraph, runs)
#time_end = datetime.datetime.fromtimestamp(time.time())
#print("Time elapsed: ", str(time_end - time_begin))
#print("Number of runs: ", runs)

def contract(graph2):
	while(len(graph2) > 2):
		#Pick a random node and one of its adjacent nodes
		#actor1 = list(graph2.values())[random.randint(0, len(graph2)-1)]
		actor1 = random.sample(list(graph2.values()), 1)[0]
		actor1Id = actor1.actorId
		actor2Id = random.sample(list(actor1.colleagues.keys()), 1)[0]
		#actor2Id = list(actor1.colleagues.keys())[random.randint(0, len(actor1.colleagues.keys()) - 1)]
		
		# Make actor 1 a super node and delete actor 2
		# Update all nodes adjacent to actor 2
		for colleagueToActor2 in graph2[actor2Id].colleagues.items():
			colleagueId = colleagueToActor2[0]
			edgeCount = colleagueToActor2[1]

			# Remove actor 2 from the list of colleagues
			del graph2[colleagueId].colleagues[actor2Id]

			# Update the number of edges to the super node, unless it is the super node
			prevEdgesToActor1 = 0
			if(actor1Id in graph2[colleagueId].colleagues):
				prevEdgesToActor1 = graph2[colleagueId].colleagues[actor1Id]
			if(not colleagueId == actor1Id):	
				graph2[colleagueId].colleagues[actor1Id] = prevEdgesToActor1 + edgeCount
				graph2[actor1Id].colleagues[colleagueId] = prevEdgesToActor1 + edgeCount
		
		#Remove node 2 from the graph and update node 1 to have contracted it
		graph2[actor1Id].contracted.extend(graph2[actor2Id].contracted)
		del graph2[actor2Id]
		
	firstActor = list(graph2.values())[0]	
	secondActor = list(graph2.values())[1]	
	return (list(firstActor.colleagues.values())[0], firstActor.contracted, secondActor.contracted)

def runContractMultipleTimes(originalGraph2, N):
	minCut = (sys.maxsize, [])
	for i in range(N):
		graphCopy = copy.deepcopy(originalGraph2)
		result = contract(graphCopy)
		print(result[0])
		if(result[0] < minCut[0]):
			minCut = result
	print("Min cut: ", minCut)
	print("Total number of nodes: ", len(result[1]) + len(result[2]))



if __name__ == "__main__":
	originalGraph = parseImdb()
	graphSize = len(originalGraph.keys())
	print("OriginalGraph size: ", graphSize)

	components = findConnectedComponents(originalGraph)
	maxlen = 0
	for component in components:
		if len(component) > maxlen:
			maxlen = len(component)
		# print("Component of size: ", len(component), ", root: ", component[0])
	print("Number of components: ", len(components))
	print("max size", maxlen)