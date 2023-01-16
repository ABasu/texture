# -*- coding: utf-8 -*- 
import logging
import numpy as np

################################################################################
def power_law_cutoff(series, window_size = 10, cutoff_slope = -1, n_features = None, sortby = 1):
	"""
	Takes a series of reverse sorted numbers or (string, number) tuples, and returns 
	the index n that is the cutoff between the steep and flat portions of the curve.
	"""
	if n_features != None:
		series = series[:n_features]
	if isinstance(series[0], tuple):
		series = [s[sortby] for s in series]
	series_y = np.array(series)
	series_x = np.linspace(1, max(series), num=len(series_y))

	for i in range(len(series) - window_size * 2):
		pre_y = series_y[i : i + window_size]
		post_y = series_y[i + window_size : i +window_size * 2]
		pre_x = series_x[i : i + window_size]
		post_x = series_x[i + window_size : i +window_size * 2]
		slopes = (pre_y - post_y) / (pre_x - post_x)
		avg_slope = np.mean(slopes)
		if avg_slope >= cutoff_slope:
			return i + window_size

	return len(series)
