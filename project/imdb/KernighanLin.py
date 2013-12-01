import logging
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

# def calc_d(A, B):
# 	D = {}
# 	for a in A:
# 		D[a] = compute_improvement(a, A, B)
# 	for b in B:
# 		D[b] = compute_improvement(a, A, B)

# 	return (D)


def kernighan_lin(A, B):
	(Da, Db) = calc_d(A, B)

	temp_a = A.copy()
	temp_b = B.copy()
	swaps = []

	old_cut = cut_size(A, B)
	logging.info("The size of the old cut is %d", old_cut)

	cut_sizes = {
		0: old_cut
	}
	for i in range(1, len(A)+1):
		# maxGain = float("-infinity")

		# e = None
		# swap = None

		# Look through all nodes - n^2
		# for n1 in temp_a:
		# 	for n2 in temp_b:
		# 		e = edge_between(n1, n2)
		# 		gain = 0
		# 		if e != None:
		# 			gain = D[n1] + D[n2] + 2 * e.weight
		# 		else:
		# 			gain = D[n1] + D[n2]

		# 		if (gain > maxGain):
		# 			maxGain = gain
		# 			swap = (n1, n2)

		n1 = max(Da, key=Da.get)
		n2 = max(Db, key=Db.get)

		swap = (n1, n2)
		if swap:
			logging.debug("Swapping %s", str(swap))

			## Lock vertices
			temp_a.remove(swap[0])
			temp_b.remove(swap[1])
			swaps.append(swap)

			## Do the actual swap (which might be reverted later, but is needed to calc the size of the new cut)
			A.remove(swap[0])
			B.add(swap[0])
			B.remove(swap[1])
			A.add(swap[1])

			swap[0].locked = True
			swap[1].locked = True

			## Calc new D values
			## Second way - recalc for all neighbours
			for (e, ne) in swap[0].neighbours:
				## Swap 0 is removed from A and put into B
				if not ne.locked:
					if ne in temp_a:
						Da[ne] = Da[ne] + e.weight
						# Da[ne] = compute_improvement(ne, A, B)
					else:
						Db[ne] = Db[ne] - e.weight
						# Db[ne] = compute_improvement(ne, A, B)
				## If ne is in neither it is locked, and we don't need to recalc

			for (e, ne) in swap[1].neighbours:
				## Swap 1 is removed from B and put into A
				# if ne in temp_a:
				if not ne.locked:
					if ne in temp_a:
						Da[ne] = Da[ne] - e.weight
						# Da[ne] = compute_improvement(ne, A, B)
					else:
						Db[ne] = Db[ne] + e.weight
						# Db[ne] = compute_improvement(ne, A, B)

			del Da[n1]
			del Db[n2]

			cut_sizes[i] = cut_size(A, B)
		else:
			break

	# Find the lowest cut
	min_i = min(cut_sizes, key=cut_sizes.get)
	
	logging.debug("K that minimizes Gi: %d", min_i)

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