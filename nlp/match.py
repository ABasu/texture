# -*- coding: utf-8 -*- 

################################################################################
def find_all(string, substrings):
	"""
	A find_all implementation for literal strings. Should be faster than regexes.
	Takes a string or a tokenized list of strings and a list of strings to be found in them.

	@param string: A string or a list of token strings
	@type  string: string or list of strings
	@param substrings: A list of literals to search for
	@type  substrings: list of strings

	@returns: list of (matchindex, matchword) tuples.
	"""
	# NOTE: Passing "" as one of the substrings to search for will result in an infinite loop
	# Do a fast check if anything occurs at all before spending time on finding position
	if any([sub in string for sub in substrings]):
		# It's either a tokenized list or a string
		if isinstance(string, list):
			indices = sorted([(i, word) for i, word in enumerate(string) if word in substrings])
		else:
			indices = []
			for sub in substrings:
				start = 0
				while True:
					start = string.find(sub, start)
					if start == -1: 
						break
					indices.append((start, sub))
					start += len(sub)
			indices = sorted(indices)
	else:
		indices = None

	return indices
		
def find_intersection(s1, s2):
	"""
	Returns the intersection (common elements) between to iterables.
	Note: When two elements of disproportionate size are being compared, making the first one the 
	shorter one seems to have a slight performance edge.
	"""
	return set(s1).intersection(s2)
