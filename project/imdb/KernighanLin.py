import logging
import operator
import heapq

class Edge:
	def __init__(self, a, b, weight = 1):
		self.weight = weight
		self.a = a
		self.b = b
		
		a.neighbours.append((self, b))
		b.neighbours.append((self, a))

	def __repr__(self):
		return str(self.a) + ' <--> ' + str(self.b)

class Node:
	def __init__(self, name):
		self.name = name
		self.neighbours = [] ## Neighbours is an array of (edge, node) tuples
		self.locked = False

	def __repr__(self):
		return self.name

	# Gives considerable speedup when using nodes in sets
	def __hash__(self):
	 	return hash(self.name)

	# Gives a speedup when checking for equality (used in edge_between)
	def __eq__(self, other):
		return self.name == other.name

# Compute the improvement of removing node from X and putting it into the other partition, aka D = E - I. This implies that node is currently found in X
def compute_improvement(node, X):
	improvement = 0
	for (e, neighbour) in node.neighbours:
		if neighbour in X:
			# internal
			improvement = improvement - e.weight
		else:
			# external
			improvement = improvement + e.weight

	return improvement

# Calculate initial D values
def calc_d(A, B):
	Da = {}
	Db = {}
	for a in A:
		Da[a] = compute_improvement(a, A)
	for b in B:
		Db[b] = compute_improvement(b, B)

	return Da, Db

def kernighan_lin(A, B):
	Da, Db = calc_d(A, B)

	swaps = []

	old_cut = cut_size(A, B)
	logging.info("The size of the old cut is %d", old_cut)

	gains = {
		0: 0
	}

	for i in range(1, len(A) + 1):
		a_largest = heapq.nlargest(3, Da.iteritems(), key=operator.itemgetter(1))
		b_largest = heapq.nlargest(3, Db.iteritems(), key=operator.itemgetter(1))

		max_gain = -10000
		for (node_a, gain_a) in a_largest:
			for (node_b, gain_b) in b_largest:
				gain = gain_a + gain_b

				if gain > max_gain:
					e = edge_between(node_a, node_b)

					if e != None:
						gain = gain - 2 * e.weight

					if gain > max_gain:
						max_gain = gain
						swap = ((node_a, gain_a), (node_b, gain_b))

		((node_a, gain_a), (node_b, gain_b)) = swap
		e = edge_between(node_a, node_b)
		logging.debug("Swapping %s", swap)

		## Lock vertices
		swaps.append(swap)

		## Do the actual swap (which might be reverted later, but is needed to calc the size of the new cut)
		A.remove(node_a)
		B.add(node_a)
		B.remove(node_b)
		A.add(node_b)

		node_a.locked = True
		node_b.locked = True

		gain = gain_a + gain_b
		if e != None:
			gain = gain - 2 * e.weight
		gains[i] = gain

		del Da[node_a]
		del Db[node_b]

		## Calc new D values
		for (e, neighbour) in node_a.neighbours:
			## node_a is removed from A and put into B. This means that for all nodes in A, external cost increases by e.weight, and their internal cost decreases by e.weight.
			## since D = E - I then D = (E + weight) - (I - weight) = E - I + 2 weight
			if not neighbour.locked:
				if neighbour in A:
					Da[neighbour] = Da[neighbour] + 2*e.weight
				else:
					Db[neighbour] = Db[neighbour] - 2*e.weight

		for (e, neighbour) in node_b.neighbours:
			## node_b is removed from B and put into A
			if not neighbour.locked:
				if neighbour in A:
					Da[neighbour] = Da[neighbour] - 2*e.weight
				else:
					Db[neighbour] = Db[neighbour] + 2*e.weight

	current_gain = 0
	max_gain = -1
	min_k = len(swaps)
	for k in range(1, len(gains)):
		current_gain = current_gain + gains[k]

		if current_gain >= max_gain:
			max_gain = current_gain
			min_k = k
	
	logging.info("K with maximum sub-sum: %d", min_k)
	logging.info("Gain for k: %d", max_gain)

	j = len(swaps)
	while j > min_k:
		j = j - 1 
		# Rewind swap
		((node_a, _), (node_b, _)) = swaps.pop()

		A.add(node_a)
		B.remove(node_a)
		B.add(node_b)
		A.remove(node_b)

	new_cut = cut_size(A, B)
	logging.debug("Final swap %s", str(swaps))
	logging.info("New cut is %d", new_cut)

	if (old_cut - new_cut > 0):
		for a in A:
			a.locked = False
		for b in B:
			b.locked = False

		kernighan_lin(A, B)

	return A, B

def edge_between(n1, n2):
	if len(n1.neighbours) > len(n2.neighbours):
		n2, n1 = n1, n2

	for (e, neighbour) in n1.neighbours:
		if neighbour == n2:
			return e

	return None

def cut_size(A, B):
	size = 0

	for n in A:
		for (e, neighbour) in n.neighbours:
			if neighbour in B:
				size = size + e.weight

	return size