# -*- coding: utf-8 -*- 

import logging
from texture.nlp.tokenize import Tokenize

################################################################################
def typetoken(text, **kwargs):
	"""
	Computes type-token ratio for a text.

	@param text: A string or list of string tokens
	@type  text: string or list
	@param kwargs: A list of keyword arguments to be passed to the Tokenize object instance.
	@type  kwargs: dict
	"""
	# If text is not tokenized, tokenize it. Otherwise we assume it's a list of strings.
	if isinstance(text, str):
		tokenizer = Tokenize(**kwargs)
		text = tokenizer.tokenize(text)

	# TTR for an empty string is None
	if text == []:
		return None
	tokens = len(text)
	types = len(set(text))

	return float(types)/ tokens

