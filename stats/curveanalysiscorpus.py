# -*- coding: utf-8 -*- 
import logging
import numpy as np
import scipy as sp
from texture.nlp.tokenize import Tokenize
from texture.corpora.bowcorpus import BOWCorpus
from texture.stats.rolling import rolling_slope
from texture.stats.rolling import rolling_avg

################################################################################
class CurveAnalysisCorpus(BOWCorpus):
	"""
	This corpus transforms a set of (usually time-series) curves into various forms.
	"""

	def __init__(self, \
			mode = 'rectangular',\
			rolling_window = 10, \
			threshold = 0.3, \
			develop = 0, \
			):

		self.mode = mode
		self.rolling_window = rolling_window
		self.threshold = threshold
		self._develop = develop

	def transform(self):

		if hasattr(self, 'corpus'):
			self.labels = self.corpus.labels
			self.filenames = self.corpus.filenames
			self.features = self.corpus.features
			self.vectors = self.corpus.vectors
			if hasattr(self.corpus, 'targets'):
				self.targets = self.corpus.targets
		# Calculate rolling average, convert to z-scores, and convert [-1, 1] scores
		vecs = [rolling_avg(v, self.rolling_window, strip_ends=False) for v in self.vectors]
		self.vectors = [sp.stats.zscore(v) for v in vecs]
		if self.mode == 'z-score':
			return self
		
		vecs = [[(-1 if v < -self.threshold else (1 if v > 0 else v)) for v in vec] for vec in self.vectors]
		# Eliminate local fluctuations
		before = 0
		between = False
		start = 0
		for vec in vecs:
			for i, v in enumerate(vec):
				if v > -1 and v < 1:
					between = True
					if not start:
						start = i
				if v in [-1, 1]:
					if between:
						after = v
						if before == after:
							vec[start:i] = [before] * (i-start)
					between = False
					before = v
					start = 0
		self.vectors = vecs
		if self.mode == 'rectangular':
			return self
		
		# Convert to rolling slope and transform into rises and falls: 1, -1
		vecs = [rolling_slope(v, self.rolling_window, strip_ends=False) for v in self.vectors]
		vecs = [[(1 if v > self.threshold else -1 if v < -self.threshold else 0) for v in vec] for vec in vecs]
		self.vectors = vecs
		if self.mode == 'transitions':
			return self

	def set_min_transitions(self, n=4):
		"""
		For 'rectangular', and 'transitions' transforms, eliminate items with more than n transitions.
		"""
		# Eliminate non-orthographic cases
		to_keep = []
		for i, vec in enumerate(self.vectors):
			nswitches = 0
			prev = 0
			for y in vec:
				if y != prev and int(y) == y:
					nswitches += 1
				prev = y
			if nswitches > n:
				to_keep.append(False)
			else:
				to_keep.append(True)
		self.vectors = [v for i, v in enumerate(self.vectors) if to_keep[i]]
		self.labels = [n for i, n in enumerate(self.labels) if to_keep[i]]
		self.filenames = [n for i, n in enumerate(self.filenames) if to_keep[i]]

		return self
