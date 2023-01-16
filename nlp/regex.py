# -*- coding: utf-8 -*- 

import re
import numpy as np

################################################################################
class Regex(object):
	"""
	Performs a set common regex operations with multiple regexes.
	"""

	def __init__(self, patterns):
		"""
		Set up a list of regex patterns.

		@param patterns: A list of regexes or (regex, subst) tuples
		@type  patterns: A list of strings or two string tuples
		"""
		# Handle single patterns not wrapped as a list
		if isinstance(patterns, tuple) or isinstance(patterns, str):
			patterns = [patterns]

		# Convert list of strings to a list of tuples
		if isinstance(patterns[0], str):
			patterns = [(p,) for p in patterns]

		# Convert to a numpy array so we can slice it
		patterns = np.array(patterns)

		self.regexes = []
		self.regexes = patterns[:, 0]

		# Check is subs have been supplied
		if len(patterns[0]) == 2:
			self.subs = patterns[:, 1:]

	def sub(self, string, match_all = False):
		"""
		Performs regex substitution on a list of regexes.
		Substitutions are in order and run throught the complete 
		list of patterns.

		@param match_all: Go thru all the subs. Otherwise, breaks on first match.
		@type  match_all: Boolean
		
		@return: The final modified string
		"""
		for i, r in enumerate(self.regexes):
			new_string = re.sub(r, self.subs[i][0], string)
			if match_all:
				string = new_string
			else:
				if string != new_string:
					string = new_string
					break

		return string

	def search(self, string):
		"""
		Searches a string for a set of patterns. Stops after the 
		first match. Returns the matchobject.
		"""
		for reg in self.regexes:
			match = re.search(reg, string)
			if match:
				return match

		return False




