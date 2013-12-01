## http://stackoverflow.com/questions/9816603/range-is-too-large-python
import itertools
range = lambda stop: iter(itertools.count().next, stop)

## http://stackoverflow.com/questions/2037327/translating-function-for-finding-all-partitions-of-a-set-from-python-to-ruby
def partitions(set_):
	y = len(set_) / 2
	for i in range(2**len(set_)/2):
		parts = [set(), set()]
		for item in set_:
			parts[i&1].add(item)
			i >>= 1
		if (len(parts[0]) == y):
			yield parts
