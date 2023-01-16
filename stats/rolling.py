# -*- coding: utf-8 -*- 

import random, logging
from scipy.stats import linregress
from scipy.stats import zscore
import numpy as np

################################################################################
def rolling_avg(vec, n, step=1, strip_ends=True):
	"""
	Takes a list of size N and calculates a rolling avg on n variables.

		>>> q = range(10)
		>>> txt.stats.rolling.rollingavg(q, 4)
		[1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5]
	"""
	rolling_vec = []
	if strip_ends:
		# turn n into a float so all averages are floating points
		window_size = float(n)

		window_sum = sum(vec[:n-1])

		for i in range(0, len(vec)-n+1, step):
			# add the last item
			window_sum += vec[i+n-1]
			avg = window_sum / window_size
			rolling_vec.append(avg)

			# Update for next cycle of the loop - drop the first item
			window_sum = window_sum - vec[i]
	else:
		for i in range(-n+1, len(vec), step):
			window = vec[i:i+n] if i >= 0 and i < len(vec) else vec[:i+n] if i < 0 else vec[i:] 
			length = float(len(window))
			avg = sum(window) / length
			rolling_vec.append(avg)

		ldiff = int((len(rolling_vec) - len(vec)) / 2)
		rolling_vec = rolling_vec[ldiff:ldiff+len(vec)]


	return np.array(rolling_vec)

################################################################################
def rolling_slope(vec, n, step=1, strip_ends=True):
	"""
	Takes a list of size N and returnes a list of rolling slopes of n elements each.
	"""
	window_size = float(n)

	rolling_vec = []
	vec = zscore(vec)

	x = zscore(list(range(n)))
	if strip_ends:
		for i in range(0, len(vec)-n+1, step):
			y = vec[i : i+n]
			m, c, r, p, e = linregress(x, y)
			# m, p = pearsonr(x, y)
			rolling_vec.append(m)
	else:
		for i in range(2, len(vec) + 2, step):
			y = vec[:i]
			y = y[i-n:]
			x = zscore(list(range(len(y))))
			m, c, r, p, e = linregress(x, y)
			rolling_vec.append(m)

	return rolling_vec

