from KernighanLin import kernighan_lin, Edge, Node, cut_size
from partition import partitions
from AlgProjctParsing import parseImdb, findConnectedComponents
import logging
import sys

logging.basicConfig(stream=sys.stderr, level=logging.INFO)

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



# print timeit.Timer("run()","from __main__ import run").timeit(5000)

originalGraph = parseImdb(400)
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
		Edge(nodes[a.id], nodes[colleague])
		edge_count = edge_count + 1

print "Edge count: ", edge_count

# Graph is not completely connected (if it is, all cuts will have the same size when edge weight is 1)
assert edge_count != node_count * (node_count - 1)

#### START BY RUNNING KL WITH INITIAL PART TAKING EVERY SECOND ELEMENT INTO EACH SET
val = nodes.values()

part_a = set(val[:len(val)/2])
part_b = set(val[len(val)/2:])

print "Running KL with initial partition (found by taking every second element)", part_a, part_b, "cut size: ", cut_size(part_a, part_b)

(new_a, new_b) = kernighan_lin(part_a, part_b)
print "KL returned new partition", new_a, new_b
print  "New cut size: ", cut_size(new_a, new_b)

# #### THEN GENERATE ALL POSSIBLE PARTITIONS TO FIND THE ACTUAL MIN
# min_cut = sys.maxint
# for p in partitions(nodes.values()):
# 	cut = cut_size(p[0], p[1])
# 	# print cut
# 	if cut < min_cut:
# 		min_cut = cut
	

# print "Actual min cut (found by looking at all possible cuts):", min_cut

# #### USE THE FIRST PARTITION FOUND BY PARTITIONS() AS INPUT TO KL TO SEE THE EFFECT OF A DIFFERENT STARTING PARTITION
# first_part = part[0]
# part_a = first_part[0]
# part_b = first_part[1]

# print "Running KL with initial partition (first partition from the generation of all partitions)", part_a, part_b, "cut size: ", cut_size(part_a, part_b)

# (new_a, new_b) = kernighan_lin(part_a, part_b)
# print "KL returned new partition", new_a, new_b
# print  "New cut size: ", cut_size(new_a, new_b)

