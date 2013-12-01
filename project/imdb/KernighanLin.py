import logging
import sys
from time import time

class Edge:
	def __init__(self, a, b, weight = 1):
		self.weight = weight
		self.a = a
		self.b = b
		
		a.edges.append(self)
		b.edges.append(self)
		a.neighbours.append((self, b))
		b.neighbours.append((self, a))

	def __repr__(self):
		return str(self.a) + ' <--> ' + str(self.b)

	# Does edge have one of its endpoints in node?
	def connected_to(self, node):
		return self.a == node or self.b == node


class Node:
	def __init__(self, name):
		self.name = name
		self.edges = []
		self.neighbours = []
		self.id = id(self)
		self.locked = False

	def __repr__(self):
		return self.name

# Compute the improvement of moving node from A to B, aka D = E - I. Node is assumed to have at least one endpoint in A
def compute_improvement(node, A, B):
	improvement = 0
	for e in node.edges:
		a_in_A = e.a in A
		b_in_A = e.b in A
		if (a_in_A and b_in_A) or (not a_in_A and not b_in_A):
			# internal
			improvement = improvement - e.weight
		else:
			# external
			improvement = improvement + e.weight

	return improvement

def calc_d(A, B):
	Da = {}
	Db = {}
	for a in A:
		Da[a] = compute_improvement(a, A, B)
	for b in B:
		Db[b] = compute_improvement(a, A, B)

	return (Da, Db)

def kernighan_lin(A, B):
	(Da, Db) = calc_d(A, B)

	swaps = []

	old_cut = cut_size(A, B)
	logging.info("The size of the old cut is %d", old_cut)

	gains = {
		0: 0
	}
	
	for i in range(1, len(A)):
		node_a = max(Da, key=Da.get)
		node_b = max(Db, key=Db.get)

		e = edge_between(node_a, node_b)

		logging.debug("Swapping %s", (node_a, node_b))

		## Lock vertices
		swaps.append((node_a, node_b))

		## Do the actual swap (which might be reverted later, but is needed to calc the size of the new cut)
		A.remove(node_a)
		B.add(node_a)
		B.remove(node_b)
		A.add(node_b)

		node_a.locked = True
		node_b.locked = True

		## Calc new D values
		for (e, ne) in node_a.neighbours:
			## node_a is removed from A and put into B. This means that for all nodes in A, external cost increases by e.weight, and their internal cost decreases by e.weight.
			## since D = E - I then D = (E + weight) - (I - weight) = E - I + 2 weight
			if not ne.locked:
				if ne in A:
					Da[ne] = Da[ne] + 2*e.weight
				else:
					Db[ne] = Db[ne] - 2*e.weight

		for (e, ne) in node_b.neighbours:
			## node_b is removed from B and put into A
			if not ne.locked:
				if ne in A:
					Da[ne] = Da[ne] - 2*e.weight
				else:
					Db[ne] = Db[ne] + 2*e.weight

		gain = Da[node_a] + Db[node_b]
		if e != None:
			gain = gain - 2 * e.weight
		gains[i] = gain

		del Da[node_a]
		del Db[node_b]

	current_gain = 0
	max_gain = -1
	min_i = -1
	for i in range(0, len(gains)):
		current_gain = current_gain + gains[i]

		if current_gain >= max_gain:
			max_gain = current_gain
			min_i = i

	
	logging.info("K with maximum sub-sum: %d", min_i)

	j = len(swaps)
	while j > min_i:
		j = j - 1 
		# Rewind swap
		swap = swaps.pop() 
		A.add(swap[0])
		B.remove(swap[0])
		B.add(swap[1])
		A.remove(swap[1])

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
	for e in n1.edges:
		if e.connected_to(n2):
			return e

	return None

def cut_size(A, B):
	size = 0

	for n in A:
		for e in n.edges:
			if (e.a in A and e.b in B) or (e.a in B and e.b in A):
				size = size + e.weight

	return size