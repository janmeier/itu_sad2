import logging
import sys
import operator

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
		self.neighbours = []
		self.locked = False

	def __repr__(self):
		return self.name

# Compute the improvement of moving node from A to B, aka D = E - I. Node is assumed to have at least one endpoint in A
def compute_improvement(node, A, B):
	improvement = 0
	for (e, _) in node.neighbours:
		if (e.a in A and e.b in A) or (e.a in B and e.b in B):
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
		Db[b] = compute_improvement(b, A, B)

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
		sorted_da = sorted(Da.iteritems(), key=operator.itemgetter(1))
		sorted_db = sorted(Db.iteritems(), key=operator.itemgetter(1))
		sorted_da.reverse()
		sorted_db.reverse()

		swap = None
		max_gain = -1000000000
		for (node_a, a_gain) in sorted_da:
			(node_b, b_gain) = sorted_db[len(sorted_db) - 1]
			if a_gain + b_gain <= max_gain:
				break
			
			for (node_b, b_gain) in sorted_db:
				if a_gain + b_gain <= max_gain:
					break
				e = edge_between(node_a, node_b)
				if e != None:
					weight = e.weight
				else:
					weight = 0

				max_gain = a_gain + b_gain - 2 * weight
				swap = (node_a, node_b)

		if swap:
			(node_a, node_b) = swap
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

			gain = Da[node_a] + Db[node_b]
			if e != None:
				gain = gain - 2 * e.weight
			gains[i] = gain

			del Da[node_a]
			del Db[node_b]

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

	current_gain = 0
	max_gain = -1
	min_i = len(swaps)
	for i in range(1, len(gains)):
		current_gain = current_gain + gains[i]

		if current_gain >= max_gain:
			max_gain = current_gain
			min_i = i
	
	logging.info("K with maximum sub-sum: %d", min_i)
	logging.info("Gain for k: %d", max_gain)

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
	for (e, ne) in n1.neighbours:
		if ne == n2:
			return e

	return None

def cut_size(A, B):
	size = 0

	for n in A:
		for (e, _) in n.neighbours:
			if (e.a in A and e.b in B) or (e.a in B and e.b in A):
				size = size + e.weight

	return size