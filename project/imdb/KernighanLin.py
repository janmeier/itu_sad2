import logging
import sys
import operator
import heapq
from time import time

class Edge:
	def __init__(self, a, b, weight = 1):
		self.weight = weight
		self.a = a
		self.b = b
		
		a.neighbours.append((self, b))
		b.neighbours.append((self, a))

	def __repr__(self):
		return str(self.a) + ' <--> ' + str(self.b)

	# def __hash__(self):
	# 	return self.a.hash() + self.b.hash()

class Node:
	def __init__(self, name):
		self.name = name
		self.neighbours = []
		self.locked = False

	def __repr__(self):
		return self.name

	def __hash__(self):
	 	return hash(self.name)

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

	sort_time = 0
	find_time = 0
	swap_time = 0
	update_time = 0

	for i in range(1, len(A) + 1):
		start = time()
		a_largest = heapq.nlargest(2, Da.iteritems(), key=operator.itemgetter(1))[1:]
		b_largest = heapq.nlargest(2, Db.iteritems(), key=operator.itemgetter(1))[1:]

		current_swaps = zip(a_largest, b_largest)
		find_time = find_time + (time() - start)

		for swap in current_swaps:
		# if swap:
			start = time()
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

			swap_time = swap_time + (time() - start)
			start = time()

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

			update_time = update_time + (time() - start)

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
	# print "Sort time ", sort_time
	# print "Find time ", find_time
	# print "Swap time", swap_time
	# print "Update time", update_time
	# print "\n\n"

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