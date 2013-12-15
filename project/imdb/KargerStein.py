import sys
import datetime, time
import random
import copy
import math
from collections import deque

# This class represents a node in our graph
class Actor:
	def __init__(self, name, actorId):
		# The name
		self.name = name
		# The id in the graph
		self.id = self.actorId = actorId
		# The adjecency list
		self.colleagues = {}
		# Can be used for listing the partitions
		self.contracted = [actorId]
		# The total sum of edges weight of this node 
		self.weight = 0

	def __repr__(self):
		return self.actorId + " " + self.name

# This class is only used for parsing the data
class Movie:
	def __init__(self, title, rating, actors):
		self.title = title
		self.rating = rating
		self.actors = actors

	def __repr__(self):
		return self.name

# Parse the file and return the graph, max_depth is used for only reading a subset of the lines
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
					addMovieToGraph(movie, graph)
				movie = Movie(movieTitle, movieId, [actor])
				lastMovieId = movieId
			i += 1	

			if i > max_depth:
				break
	return graph

# Adds edges between all the actors of this movie
def addMovieToGraph(movie, graph):
	# Make sure all actors in this movie are added to the graph
	for actor in movie.actors:
		if(not actor.actorId in graph):
			graph[actor.actorId] = actor
	# Add edges between all actors
	for actor1 in movie.actors:
		for actor2 in movie.actors:
			if(actor1.actorId != actor2.actorId):
				# Add an edge bewteen them, 1 means one edge (used for contraction)
				actor1.weight += 1
				if not actor2.actorId in graph[actor1.actorId].colleagues: 
					graph[actor1.actorId].colleagues[actor2.actorId] = 1
				else:
					graph[actor1.actorId].colleagues[actor2.actorId] += 1

# Simple bredth first search used to identify connected components
def bfs(graph, root):
	q = deque() # The queue of nodes to visit
	v = {} # The nodes already visited
	q.append(root)
	v[root] = 1
	while(len(q) > 0):
		actor1 = graph[q.popleft()]
		for actor2Id in actor1.colleagues:
			if(not actor2Id in v):
				v[actor2Id] = 1
				q.append(actor2Id)
	return v

# Find all connected components of the graph
def findConnectedComponents(graph):
	graphSize = len(graph)
	nodes = {x: 1 for x in graph.keys()}
	components = []
	found = 0
	while(found < graphSize):
		root = list(nodes)[0]
		visited = bfs(graph, root)
		found += len(visited)
		components.append(list(visited))
		for node in visited:
			del nodes[node]
	return components

# Delete a node and all it entries in adjacency lists
def deleteNode(graph, actorId):
	for actor2Id in graph[actorId].colleagues:
		w = graph[actor2Id].colleagues[actorId]
		graph[actor2Id].weight -= w
		del graph[actor2Id].colleagues[actorId]
	del graph[actorId]

# Finds a random edge in the graph in O(n)
def findRandomEdge(graph):
	actor1Id = -1
	actor2Id = -1
	totalWeight = 0
	
	# Find the total weight of the graph
	for actor in graph.values():
		totalWeight += actor.weight
	
	# Find a node to be the start point of the edge
	r = random.randint(0, totalWeight-1)
	for actor in graph.items():
		if r < 0:
			break
		actor1Id = actor[0]
		r -= actor[1].weight

	# Find a node to be the end point of the edge
	totalWeight = graph[actor1Id].weight
	r = random.randint(0, totalWeight-1) 
	for colleague in graph[actor1Id].colleagues.items():
		if r < 0:
			break
		actor2Id = colleague[0]
		r -= colleague[1]
	
	return (actor1Id, actor2Id)	

# Contract the graph to n edges (n is 2 by default)	
def contract(graph, n = 2):
	while(len(graph) > n):
		#Pick a random node and one of its adjacent nodes
		(actor1Id, actor2Id) = findRandomEdge(graph)

		# Make actor 1 a super node and delete actor 2
		# Update all nodes adjacent to actor 2
		for colleagueToActor2 in graph[actor2Id].colleagues.items():
			colleagueId = colleagueToActor2[0]
			edgeCount = colleagueToActor2[1]

			# Remove actor 2 from the list of colleagues
			del graph[colleagueId].colleagues[actor2Id]

			# Update the number of edges to the super node, unless it is the super node
			prevEdgesToActor1 = 0
			if(actor1Id in graph[colleagueId].colleagues):
				prevEdgesToActor1 = graph[colleagueId].colleagues[actor1Id]
			if(not colleagueId == actor1Id):	
				graph[colleagueId].colleagues[actor1Id] = prevEdgesToActor1 + edgeCount
				graph[actor1Id].colleagues[colleagueId] = prevEdgesToActor1 + edgeCount
		
		#Remove node 2 from the graph and update node 1 to have contracted it
		graph[actor1Id].contracted.extend(graph[actor2Id].contracted)
		del graph[actor2Id]
		
	return graph

# Recursive contract as defined by Karger-Stein
def recursiveContract(graph, n, minCuts):
	if len(graph) < 7:
		# Contract the graph down to two edges
		g = contract(graph)
		firstActor = graph.values()[0]	
		secondActor = graph.values()[1]	
		numberOfActors = min(len(firstActor.contracted), len(secondActor.contracted))
		result = list(firstActor.colleagues.values())[0]
		
		# Store this result if it is the smallest found for this partition size
		if numberOfActors in minCuts:
			if result < minCuts[numberOfActors]:
				minCuts[numberOfActors] = result
		else:
			minCuts[numberOfActors] = result

	else:
		graphCopy = copy.deepcopy(graph)
		newN = int((n/(math.sqrt(2))) + 2) #+2 because int() will round down and we want to round up 
		g1 = contract(graph, newN)
		g2 = contract(graphCopy, newN)
		recursiveContract(g1, newN, minCuts)
		recursiveContract(g2, newN, minCuts)

# Runs the recusive-contract algorithm log^2(n) times and prints the result
def runRecursiveContractMultipleTimes(graph):
	minCuts = {}
	n = int(math.ceil(math.log(len(graph), 10) * math.log(len(graph), 10)))
	for i in range(n):
		graphCopy = copy.deepcopy(graph)
		recursiveContract(graphCopy, len(graphCopy), minCuts)
	print("Min cuts:")
	for cut in minCuts.items():
		print(cut[0], cut[1])


# Parse the graph	
originalGraph = parseImdb(600)
graphSize = len(originalGraph)
print("Original graph size: ", graphSize)
edges = 0
for actor in originalGraph.values():
	edges += actor.weight
print("Edges: ", edges/2)

# Find the largest component
components = findConnectedComponents(originalGraph)
maxlen = 0
index = 0
maxIndex = 0
for component in components:
	if len(component) > maxlen:
		maxlen = len(component)
		maxIndex = index
	index += 1

print("Number of components: ", len(components))
print("max size", maxlen)
for i in range(len(components)):
	if(not i == maxIndex):
		for actorId in components[i]:
			deleteNode(originalGraph, actorId)

N = len(originalGraph)
edges = 0
for actor in originalGraph.values():
	edges += len(actor.colleagues)
print("Length of graph: ", N)
print("Edges: ", edges/2)

# Run the algorithm
runRecursiveContractMultipleTimes(originalGraph)