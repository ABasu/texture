# -*- coding: utf-8 -*- 
import logging
import numpy as np

################################################################################
class Scale(object):
	"""
	Performs scaling of lists or individual numbers. Performs linear scaling by 
	default. But can take a function and a domain within that function and scale 
	all inputs to within those limits. 
	
	For example, supplying a cos function and a domain of pi to 2pi scales all 
	values to an S curve. The 'cosine' and 'log' functions are built in. 
	'cosine' generates the s-curve of the cosine function between pi and 2pi and 
	'log' generates a log curve between 1 and 100 by default.
	"""
	def __init__(self, \
			sdomain = ('min', 'max'), \
			srange = (0, 1), \
			clamp = False, \
			function = 'linear', \
			function_domain = None):
		"""
		@param sdomain: The minimum and maximum limit for the input domain. 
		Can be set as 'min' and 'max' to use the lower and upper limits of the 
		supplied list of numbers.
		@type  sdomain: tuple of numbers or 'min'/'max'
		@param srange: The lower and upper limit of the output scale.
		@type  srange: tuple of numbers 
		@param clamp: Designates whether or not input values that fall outside 
		the domain should be clamped to their minimum or maximum values.
		@type  clamp: boolean
		@param function: Denotes the scaling function to be used. Cosine produces 
		a cosine-wave pattern from low to high. 
		@type  function: string or function. String can be 'linear', 'cosine', or
		'log'
		@param function_domain: The domain within which the transformation function 
		should be applied
		@type  function_domain: tuple of numbers

		>>> scaler = txt.stats.scale.Scale()
		scaler.scale([1,2,3,4])
		[0.0, 0.3333333333333333, 0.6666666666666666, 1.0]

		>>> scaler = txt.stats.scale.Scale(sdomain=(0,100), srange=(0,10))
		scaler.scale([1,20,33,40, 150])
		[0.1, 2.0, 3.3, 4.0, 15.0]

		>>> scaler = txt.stats.scale.Scale(sdomain=(0,100), srange=(0,10), clamp=True)
		scaler.scale([1,20,33,40, 150])
		[0.1, 2.0, 3.3, 4.0, 10.0]

		>>> scaler = txt.stats.scale.Scale(sdomain=(0,5), srange=(0,50), clamp=True, function='cosine')
		scaler.scale(range(5))
		[0.0, 4.7745751406263137, 17.274575140626311, 32.725424859373682, 45.225424859373689]

		>>> scaler = txt.stats.scale.Scale(sdomain=(0,5), srange=(0,50), clamp=True, function=lambda x: x**2, function_domain=(-5, 0))
		scaler.scale(range(5))
		[0.0, 2.952, 4.352, 4.872, 4.992]

		"""
		self.dmin = sdomain[0]
		self.dmax = sdomain[1]
		self.rmin = float(srange[0])
		self.rmax = float(srange[1])

		self.clamp = clamp
		self.function = function
		self.function_domain = function_domain

	def scale(self, series):
		"""
		This function accepts a single number or a list of numbers and returns a 
		scaled number or list according to the set parameters.

		@param series: A single number or a list of numbers to be scaled
		@type  series: number or list of numbers

		@returns: Scaled number or list
		"""
		# Make sure we handle single numbers 
		if not isinstance(series, list):
			series = [series]
			unwrap = True
		else:
			unwrap = False

		if self.function == 'linear':
			series = self.scale_linear(series)
		else:
			if self.function == 'cosine':
				self.function = np.cos
				if not self.function_domain:
					self.function_domain = (np.pi, 2*np.pi)
			elif self.function == 'log':
				self.function = np.log
				if not self.function_domain:
					self.function_domain = (1,100)
			series = self.scale_func(series)

		# If a single number was supplied, unwrap the list 
		if unwrap:
			series = series[0]

		return series

	def scale_linear(self, series):
		"""
		Scales the series linearly.
		"""
		dmin = float(np.min(series)) if self.dmin == 'min' else float(self.dmin)
		dmax = float(np.max(series)) if self.dmax == 'max' else float(self.dmax)
		if dmin == dmax:
			logging.warning('Domain is 0')

		dspan = dmax - dmin
		rspan = float(self.rmax) - float(self.rmin)
		
		# The main scaling loop
		series = [self.rmin + (n - dmin) * rspan/dspan for n in series]
		# Implement clamping for maximum and minimum values, if set
		if self.clamp:
			series = [n if n>=self.rmin and n<=self.rmax else self.rmin if n<self.rmin else self.rmax for n in series]

		return np.array(series)

	def scale_func(self, series):
		"""
		Scales the series on a cosine function. First scales the series from pi to 2*pi. Then 
		calculates cosine of each value. Finally scales linearly to target range again.
		"""
		# First, use linear scaling to map values to the function_domain
		linear_scaler = self.__class__(sdomain=(self.dmin, self.dmax), srange=self.function_domain, clamp=self.clamp, function='linear')
		series = linear_scaler.scale(series)
		# Apply function
		series = [self.function(s) for s in series]
		# Linearly scale results to the output domain
		scale_domain = (self.function(self.function_domain[0]), self.function(self.function_domain[1]))
		linear_scaler = self.__class__(sdomain=(scale_domain), srange=(self.rmin, self.rmax), clamp=self.clamp, function='linear')
		series = linear_scaler.scale(series)

		return series
