import logging

class Edge:
	def __init__(self, a, b, weight = 1):
		self.weight = weight
		self.a = a
		self.b = b

		a.edges.append(self)
		b.edges.append(self)
		a.neighbours.append(b)
		b.neighbours.append(a)

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

	def __repr__(self):
		return self.name

# Compute the improvement of moving node from A to B, aka D = E - I. Node is assumed to have at least one endpoint in A
def compute_improvement(node, A, B):
	improvement = 0
	for e in node.edges:
		if (e.a in A and e.b in A) or (e.a in B and e.b in B):
			# internal
			improvement = improvement - e.weight
		else:
			# external
			improvement = improvement + e.weight

	return improvement

def calc_d(A, B):
	D = {}
	for a in A:
		D[a] = compute_improvement(a, A, B)
	for b in B:
		D[b] = compute_improvement(a, A, B)

	return (D)

def kernighan_lin(A, B):
	(D) = calc_d(A, B)

	temp_a = A.copy()
	temp_b = B.copy()
	swaps = []

	old_cut = cut_size(A, B)
	logging.info("The size of the old cut is %d", old_cut)

	gains = {

	}
	cut_sizes = {
		0: old_cut
	}
	for i in range(1, len(A)+1):
		maxGain = float("-infinity")

		e = None
		swap = None

		# Look through all nodes - n^2
		for n1 in temp_a:
			for n2 in temp_b:
				e = edge_between(n1, n2)
				gain = 0
				if e != None:
					gain = D[n1] + D[n2] + 2 * e.weight
				else:
					gain = D[n1] + D[n2]

				if (gain > maxGain):
					maxGain = gain
					swap = (n1, n2)

		# n1 = max(Da, key=Da.get)
		# n2 = max(Db, key=Db.get)
		# swap = (n1, n2)
		if swap:
			logging.debug("Swapping %s", str(swap))
			## Lock vertices
			temp_a.remove(swap[0])
			temp_b.remove(swap[1])
			swaps.append(swap)

			## Do the actual swap (which might be reverted later, but is needed to calc new D values)
			A.remove(swap[0])
			B.add(swap[0])
			B.remove(swap[1])
			A.add(swap[1])

			## Calc new D values

			## First way - recalc all
			# (D) = calc_d(temp_a, temp_b)


			## Second way - recalc for all neighbours
			for ne in swap[0].neighbours + swap[1].neighbours:
				D[ne] = compute_improvement(ne, A, B)


			cut_sizes[i] = cut_size(A, B)
			gains[i] =  maxGain
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