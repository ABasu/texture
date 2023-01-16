# -*- coding: utf-8 -*- 

import random, logging

################################################################################
def chunk_list(clist, csize = None, nchunks = None, shuffle = False):
	"""
	Takes a list and returns chunks of approx size 'csize'. 
	If shuffle is set to True, then items in the list are shuffled before drawing. 
	We can take a list of 10 items and ask for chunks of approximate length 4 etc. 
	Used to shuffle text chunks or filenames.

	@param clist: A list e.g. of tokenized text.
	@type  clist: list
	@param csize: The approximate size of chunks. 
	@type  csize: int
	@param nchunks: The number of chunks. If this is set then we ignore csize.
	@type  nchunks: int
	@param shuffle: Whether or not to shuffle the chunks. B{Default:} True
	@type  shuffle: boolean

	@return: C{yields} lists.
	"""
	if shuffle:
		# make a copy of list before shuffling to leave the original untouched
		clist = list(clist)
		random.shuffle(clist)

	chunks = []

	# If nchunks isn't set, then we want to generate chunks of approx csize. 
	# Otherwise we simply ignore csize.
	if not nchunks:
		nchunks = len(clist) / csize
	if not csize:
		csize = len(clist) / nchunks

	
	# If clist is greater than the length of the list, there's only one chunk.
	if nchunks == 0:
		yield clist
	else:
		csize += int(len(clist) % csize) / nchunks
		for i in range(nchunks - 1):
			yield(clist[i * csize : (i + 1) * csize])
		yield(clist[(nchunks - 1) * csize :])

################################################################################
def random_sample_list(slist, ssize, upscale = False):
	"""
	Generates a sample of ssize randomly from a list. If number of samples is more
	than the size of the list then the list is upscaled. 

	@param slist: A list - e.g tokenized text.
	@type  slist: list
	@param ssize: Size of the sample. If this is less than the size of slist, the list is upscaled with a warning.
	@type  ssize: int

	@return: list of samples.
	"""
	if(ssize > len(slist)):
		if upscale:
			# logging.warning("Sample is larger than population to choose from. Upscaling population - elements will be repeated.")
			factor = (ssize / len(slist)) + 1
			slist = slist * factor
		else:
			# logging.warning("Sample is larger than population and upscaling is turned off - returning entire population.")
			ssize = len(slist)

	return random.sample(slist, ssize)
