from KernighanLin import kernighan_lin, Edge, Node, cut_size
from partition import partitions
from AlgProjctParsing import parseImdb, findConnectedComponents
from random import randint
from random import shuffle
import logging
import timeit
import sys

logging.basicConfig(stream=sys.stderr, level=logging.CRITICAL)


def simpleGraphs():
	a = Node("a")
	b = Node("b")
	c = Node("c")
	d = Node("d")
	e = Node("e")
	f = Node("f")
	g = Node("g")
	h = Node("h")
	i = Node("i")
	j = Node("j")
	k = Node("k")
	l = Node("l")

	Edge(a, b)
	Edge(a, k)
	Edge(b, c)
	Edge(k, l)
	Edge(j, i)
	Edge(h, g)
	Edge(f, g)
	Edge(e, b)
	Edge(d, e)
	Edge(k, j)
	Edge(k, g)

	part_a = set([a, c, e, g, i, k])
	part_b = set([b, d, f, h, j, l])
	print "Running KL with initial partition", part_a, part_b, "cut size: ", cut_size(part_a, part_b)

	(new_a, new_b) = kernighan_lin(part_a, part_b)
	print "KL returned new partition", new_a, new_b
	print  "New cut size: ", cut_size(new_a, new_b)

	part_a = set([a, h, f, g, l, k])
	part_b = set([b, d, e, c, j, i])
	print "Running KL with initial partition", part_a, part_b, "cut size: ", cut_size(part_a, part_b)

	(new_a, new_b) = kernighan_lin(part_a, part_b)
	print "KL returned new partition", new_a, new_b
	print  "New cut size: ", cut_size(new_a, new_b)

# simpleGraphs()


originalGraph = parseImdb(3500)
graphSize = len(originalGraph.keys())
print "OriginalGraph size: ", graphSize

components = findConnectedComponents(originalGraph)
maxlen = 0
for component in components:
	if len(component) > maxlen:
		maxlen = len(component)
		max_component = component
	# print("Component of size: ", len(component), ", root: ", component[0])
print "Number of components: ", len(components)
print "Max connected component: ", maxlen

# Create nodes
nodes = {}
node_count = 0
for actor in max_component:
	nodes[actor] = Node(actor)
	node_count = node_count + 1

print "Node count :", node_count

# Then create edges
edge_count = 0
for actor in max_component:
	a = originalGraph[actor]
	for colleague in a.colleagues:
		if (actor < colleague):
		# if randint(0, 9) >= 5:
			Edge(nodes[a.id], nodes[colleague], a.colleagues[colleague])
			edge_count = edge_count + 1

print "Edge count: ", edge_count

# Graph is not completely connected (if it is, all cuts will have the same size when edge weight is 1)
assert edge_count != node_count * (node_count - 1)

#### START BY RUNNING KL WITH INITIAL PART TAKING EVERY SECOND ELEMENT INTO EACH SET
val = nodes.values()


def run():
	part_a = set(val[:len(val)/2])
	part_b = set(val[len(val)/2:])
	(new_a, new_b) = kernighan_lin(part_a, part_b)

part_a = set(val[:len(val)/2])
part_b = set(val[len(val)/2:])

# origs = []
# news = []
# for i in range(0, 100):
# 	shuffle(val)

# 	part_a = set(val[:len(val)/2])
# 	part_b = set(val[len(val)/2:])

# 	sz = cut_size(part_a, part_b)

# 	origs.append(sz)
# 	(new_a, new_b) = kernighan_lin(part_a, part_b)
# 	sz = cut_size(new_a, new_b)
# 	news.append(sz)
# 	print i

# for o in origs:
# 	print o

# for n in news:
# 	print n


print "Running KL with initial partition (found by taking every second element) cut size: ", cut_size(part_a, part_b)
(new_a, new_b) = kernighan_lin(part_a, part_b)
print "KL returned new partition with cut size: ", cut_size(new_a, new_b)

print timeit.Timer("run()","from __main__ import run").timeit(100)
