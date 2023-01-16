# -*- coding: utf-8 -*- 
import logging
import numpy as np
from texture.stats.scale import Scale
from texture.stats.rolling import rolling_avg

################################################################################
class RelativeRarity:
	# Takes a time series of absolute scores and computes the relative rarity score per year
	# May be initialized with a time series of total words per year to make RF calculations
	# possible.
	# What makes a word rare? 
	
	def __init__(self, ntokens, ndocs, window=20, year_weight=.3, window_weight=.5, first_use=False):
		"""
		@param ntokens: A list containing the total number of tokens for each year
		@type  ntokens: list of ints
		@param ndocs: A list of the total number of documents for each year.
		@type  ndocs: list of ints
		@param window: The range of 'influence' over which local log(n/df) is calculated.
		@type  window: int
		@param year_weight: The weight given to the yearly score
		@type  year_weight: float between 0.0 and 1.0
		@param window_weight: The weight given to the sliding window
		@type  window_weight: float between 0.0 and 1.0
		@param first_use: Sets every score before first use to 1
		@type  first_use: boolean
		"""
		self.ntokens = np.array(ntokens)
		self.ntokens[self.ntokens==0.0] = 1

		self.ndocs = np.array(ndocs)
		self.ndocs[self.ndocs==0] = 1

		self.window = window
		self.year_weight = year_weight
		self.window_weight = window_weight
		self.first_use = first_use

		self.scale = Scale(sdomain=(0, 'max')).scale

		m_df = np.median(self.ndocs)
		avg_ndocs =  rolling_avg(self.ndocs, window, strip_ends=False)

		self.skew_weights = np.log10(m_df * m_df / self.ndocs)
		self.skew_weights = rolling_avg(self.skew_weights, window, strip_ends=False)

	def transform(self, tfs, dfs, debug=False):
		"""
		@param tfs: term frequencies for token
		@type  tfs: list of ints
		@param dfs: document frequencies for single term
		@type  dfs: list if ints
		"""
		# Are we dealing with a word not in the db?
		# We assume it's very rare
		if np.sum(tfs) == 0:
			return np.ones(len(tfs))

		dfs = np.array(dfs)
		dfs[dfs==0] = 1

		itfs = self.get_inverted_tfs(tfs)
		yearly_tfidfs = self.get_year_weights(itfs, dfs, tfs_inverted=True)
		window_tfidfs = self.get_window_weights(itfs, dfs, tfs_inverted=True)
		
		# scores = (itfs + yearly_tfidfs * self.year_weight + window_tfidfs * self.window_weight) / (1.0 + self.year_weight + self.window_weight)
		# The formula below multiplies itfs by the weights to exaggerate their effect
		scores = (itfs * (yearly_tfidfs / self.year_weight) * (window_tfidfs / self.window_weight)) * self.skew_weights 
		scores = self.scale(scores)

		if self.first_use:
			first_use = self.get_first_use(tfs)
			scores[:first_use+1] = 1

		# Save the scores for debugging -- these are used to generate plots when generate_report is called
		if debug:
			self.itfs = itfs
			self.yearly_tfidfs = yearly_tfidfs
			self.window_tfidfs = window_tfidfs

		# return scores, itfs, yearly_tfidfs, window_tfidfs
		return scores

	def get_first_use(self, tfs):
		"""
		Return index of first nonzero year
		"""
		return np.nonzero(tfs!=0)[0][0]

	def get_inverted_tfs(self, tfs):
		rank = self.get_rank(tfs) 
		rank = 1 if rank < 1 else rank
		max = np.max(tfs) * rank
		scale = Scale(sdomain=(0, max)).scale
		# Convert to inverted relative freqs trend and scale from 0 to 1
		tfs = np.array(tfs)
		tfs = rolling_avg(tfs, self.window, strip_ends=False)
		tfs = 1.0 - scale(tfs)

		return tfs

	def get_year_weights(self, tfs, dfs, tfs_inverted=False):
		"""
		Calculates per yer log(n/df) weights for time series
		When called externally with raw tfs, tfs_inverted should be 
		set to 0 (the default) so the inversion will be done on the fly.
		"""
		if not tfs_inverted:
			tfs = self.get_inverted_tfs(tfs)
		# Calculated log(N/df) for each year
		yearly_idfs = np.log(self.ndocs/dfs)
		yearly_tfidfs = tfs * yearly_idfs
		yearly_tfidfs = yearly_tfidfs * self.skew_weights
		yearly_tfidfs = rolling_avg(yearly_tfidfs, self.window, strip_ends=False)
		# yearly_tfidfs = self.scale(yearly_tfidfs)

		return yearly_tfidfs

	def get_window_weights(self, tfs, dfs, tfs_inverted=False):
		"""
		Calculates log(n/df) weights for time series over a sliding window.
		When called externally with raw tfs, tfs_inverted should be 
		set to 0 (the default) so the inversion will be done on the fly.
		"""
		if not tfs_inverted:
			tfs = self.get_inverted_tfs(tfs)

		# Compute a weigted log(N/df) over a sliding window of years
		window_tfidfs = np.array([])
		for ypos in range(1, len(tfs)+1):
			start = 0 if ypos-self.window < 0 else ypos-self.window
			win = dfs[start:ypos]
			df = np.sum(win)
			n = np.sum(self.ndocs[start:ypos])
			ndf = n / df
			idfs = np.log(ndf)
			window_tfidfs = np.append(window_tfidfs, idfs)
		#window_tfidfs = window_tfidfs * self.skew_weights
		window_tfidfs = rolling_avg(window_tfidfs, self.window, strip_ends=False)
		# window_tfidfs = self.scale(window_tfidfs)

		return window_tfidfs

	def get_rank(self, tfs):
		"""
		Rank r = log2(f1/fn) where f1, is the top ranked word - 'the' for English corpora with 
		f1 = .05
		"""
		tf = np.float(np.sum(tfs)) / np.sum(self.ntokens)
		f1 = .05
		return np.log2(f1/tf)

	def generate_report(self, tfs, dfs, filename='rarity_report'):
		scores = self.transform(tfs, dfs, debug=True)
		
		print(("Rank for token is {}.".format(self.get_rank(tfs))))
		# pt = LinePlot(zip(range(len(scores)), scores), filename=filename+'_rarity.png').draw().save()
		# pt = LinePlot(zip(range(len(scores)), self.itfs), filename=filename+'_itfs.png').draw().save()
		# pt = LinePlot(zip(range(len(scores)), self.yearly_tfidfs), filename=filename+'_yearlytfidfs.png').draw().save()
		# pt = LinePlot(zip(range(len(scores)), self.window_tfidfs), filename=filename+'_windowtfidfs.png').draw().save()
		# pt = LinePlot(zip(range(len(scores)), self.skew_weights), filename=filename+'_skewweights.png').draw().save()

		print(("{:>10}{:>10}{:>10}{:>10}{:>10}{:>10}{:>10}{:>10}{:>10}{:>10}".format("Year", "TF", "DF", "NTokens", "NDocs", "Rarity", "ITF", "YEAR", "WINDOW", "SKEW"))) 
		for i, y in enumerate(tfs):
			print(("{:10d}{:10.0f}{:10.0f}{:10.0f}{:10.0f}{:10.3f}{:10.3f}{:10.3f}{:10.3f}{:10.3f}".format(i, tfs[i], dfs[i], self.ntokens[i], self.ndocs[i], scores[i], self.itfs[i], self.yearly_tfidfs[i], self.window_tfidfs[i], self.skew_weights[i])))
