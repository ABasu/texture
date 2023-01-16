# -*- coding: utf-8 -*-

import logging
import numpy as np

################################################################################
class GiniCoeff(object):
	"""
	Computes the Gini coefficient for a list of numbers.
	"""
	
	@staticmethod
	def gini(nums):
		"""
		Computes the Gini Coefficient for a list of numbers.
		"""
		if not isinstance(nums, list):
			x = np.array(nums)[0].tolist()
		else:
			x = nums
		n = len(x)
		x.sort()  # increasing order
		G = sum( xi * (n-i) for i,xi in enumerate(x) )  #Bgross
		G = 2.0*G/(n*sum(x))
		return 1 + (1./n) - G

		
