# -*- coding: utf-8 -*- 

import random
from texture.corpora.bowcorpus import BOWCorpus

################################################################################
class ChunkCorpus(BOWCorpus):
	"""
	Splits a corpus into chunks.

	ChunkCorpus can be used to split texts in the corpus into chunks of n words each or n number of chunks.
	N can be specified as an integer or as a percentage of the total length. Can also generate overlapping chunks
	to create sliding windows through the texts. 
	"""
	def __init__(self, \
			*args, \
			**kwargs \
			):
		# Run the parent's init
		super(ChunkCorpus, self).__init__(*args, **kwargs)

		# Set defaults for params
		self.chunksize = 1.0
		self.nchunks = None
		self.overlap = 0
		self.roundedsize = False
		self.minsize = False
		self.upscale = False

		# Make sure tokenization is turned on and initialize the chunkindices table
		# This table will contain a list of [(start, stop) tuples is a text has already been chunked
		# Otherwise it'll be None
		self.set_params(tokenize=True)

	def fit(self, \
			*args, \
			**kwargs \
			):
		# Run the parent's init
		super(ChunkCorpus, self).fit(*args, **kwargs)

		# Initialize the chunk index points list
		self.chunkindices = [None] * len(self.texts)

		return self

	def set_params(self, \
			chunksize = None, \
			nchunks = None, \
			overlap = None, \
			roundedsize = None, \
			minsize = None, \
			upscale = None, \
			**kwargs
			):
		"""
		@param chunksize: Size of chunk in number of words.
			- int: denotes chunksize in words.
			- float: Denote percentage of size (between 0.0 and 1.0).
		@type  chunksize: int or float
		@param nchunks: Number of chunks. Either this or chunksize should be set, not both.
		@type  nchunks: int
		@param overlap: The degree by which chunks overlap with each other.
			- int: Denotes number of words overlapping (must be less than chunksize).
			- float: Denotes what percentage of the chunk should overlap (between 0.0 and 1.0).
		@type  overlap: int or float
		@param roundedsize: If true then extra words are distributed roughly equally among chunks.
			Otherwise they are left out.
		@type  roundedsize: boolean
		@param minsize: Suppress texts less than chunk size when this is set to true
		@type  minsize: boolean
		@param upscale: Sample up chunks smaller than required size
		@type  upscale: boolean

		"""
		self.chunksize = self.chunksize if chunksize == None else chunksize
		self.nchunks = self.nchunks if nchunks == None else nchunks
		self.overlap = self.overlap if overlap == None else overlap
		self.roundedsize = self.roundedsize if roundedsize == None else overlap
		self.minsize = self.minsize if minsize == None else minsize
		self.upscale = self.upscale if upscale == None else upscale

		# If any of the above parameters have been changed, we need to reset existing chunkindices
		if chunksize or nchunks or overlap or roundedsize or minsize or upscale:
			self.chunkindices = [None] * len(self.texts)

		super(ChunkCorpus, self).set_params(**kwargs)

		return self

	def __iter__(self):
		for i, (label, text) in enumerate(super(ChunkCorpus, self).__iter__()):
			for (l, t) in self.chunk_text(label, text, i):
				yield (l, t)

	def __getitem__(self, key):
		texts = []
		if isinstance(key, slice):
			for i, (label, text) in enumerate(super(ChunkCorpus, self).__getitem__(key)):
				for (l, t) in self.chunk_text(label, text, i):
					texts.append((l, t))
		else:
			label, text = super(ChunkCorpus, self).__getitem__(key)
			for (l, t) in self.chunk_text(label, text, key):
				texts.append((l, t))

		return texts

	def chunk_text(self, label, text, index):
		"""
		Performs chunking on single texts and saves start_stop indices to self.chunkindices
		"""
		if self.chunkindices[index] == None:
			text_len = len(text)
			if text_len == 0:
				chunk = None
			else:
				# If nchunks has been set, use it to calculate chunksize
				# NChunks can only be an int
				if self.nchunks:
					chunksize = int(text_len / nchunks)
				# If chunksize is set instead we have to check if it's a float or int
				else:
					# if chunksize or overlap are percentages, convert to a wordcount
					if isinstance(self.chunksize, float):
						chunksize = int(text_len * self.chunksize)
					else:
						chunksize = self.chunksize
			if isinstance(self.overlap, float):
				overlap = int(self.overlap * chunksize)
			else:
				overlap = self.overlap
			
			# If the text is smaller than the size we want
			if chunksize > text_len:
				# We have a small text that is non-empty
				# If minsize is implemented, we return None. Otherwise we either scale up the
				# text or return it as is
				if self.minsize:
					chunk = None
				elif self.upscale:
					factor = (chunksize / text_len) + 1
					chunk = random.sample(text*factor, chunksize)
				else:
					chunk = text
			# Otherwise we need to do conventional chunking
			else:
				step = (chunksize-overlap) if overlap != 0 else chunksize
				starts = list(range(0, text_len - chunksize + 1, step))
				stops = [s+chunksize for s in starts]
				if self.roundedsize:
					# How many do we have left over?
					n_leftover = text_len - stops[-1]
					to_add = n_leftover/len(starts)
					if to_add:
						starts = [s+(i*to_add) for i, s in enumerate(starts)]
						stops = [s+((i+1)*to_add) for i, s in enumerate(stops)]
					n_leftover = n_leftover % len(starts)
					if n_leftover:
						starts = [s+(i*1) if i<n_leftover else s+n_leftover  for i, s in enumerate(starts)]
						stops = [s+((i+1)*1) if i<n_leftover else s+n_leftover  for i, s in enumerate(stops)]

				self.chunkindices[index] = list(zip(starts, stops))

		# If the chunkindex is still None then we have a short text handled above
		if self.chunkindices[index] == None:
			yield (label, chunk)
		else:
			# Generate label, text pairs
			for n, (start, stop) in enumerate(self.chunkindices[index]):
				l = '%s_%04d' % (label, n)
				t = text[start: stop]
				yield (l, t)
