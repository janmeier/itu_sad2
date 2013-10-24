import re

with open('imdb-r.txt') as f:
	output = None
	for line in f:
		if (line.startswith('LOCK TABLES')):
			name = re.search(r'LOCK TABLES \`(.*?)\`', line).group(1)

			if (output):
				output.close()
			output = open(name + '.txt', 'a')
		else:
			output.write(line)
	output.close()