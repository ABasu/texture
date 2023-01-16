# -*- coding: utf-8 -*- 

import logging, os
from texture.corpora.bowcorpus import BOWCorpus

################################################################################
class DramaCorpus(BOWCorpus):
	"""
	A corpus for structured playtexts. This class is initialized with a parse_play
	function that forms an interface to the actual files and returns a list of 
	dictionaries representing the play. This class will serve up text generated from
	this list.

	parse_play returns a lis of dictionaries. Each dict entry will have a 'type' 
	from ('character'|'location'|'stagedir'|'speech'). Each type has the following 
	attributes:
	* 'character': 'name', 'gender', 'short'
	* 'location': 'act', 'scene', 'text'
	* 'stagedir': 'act', 'scene', 'text'
	* 'speech': 'act', 'scene', 'text', 'speaker'
	"""
	def __init__(self, play_parser, \
			*args, \
			**kwargs \
			):
		# Run the parent's init
		super(DramaCorpus, self).__init__()

		self.play_parser = play_parser

		# Set defaults for params
		self.act = []
		self.scene = []
		self.speaker = []
		self.merge = True
		
		self.corpus_tokenize = False

		# Make sure tokenization is turned off
		self.set_params(tokenize=False)

	def set_params(self, \
			act = None, \
			scene = None, \
			speaker = None, \
			merge = None, \
			**kwargs):

		self.act = self.act if act == None else act
		self.scene = self.scene if scene == None else scene
		self.speaker = self.speaker if speaker == None else speaker
		self.merge = self.merge if merge == None else merge

		# If tokenization is set, we don't pass it up to BOWCorpus but will handle it locally.
		if 'tokenize' in kwargs and kwargs['tokenize']==True:
			self.corpus_tokenize = kwargs['tokenize']
			kwargs.pop('tokenize')
		
		super(DramaCorpus, self).set_params(**kwargs)

		return self

	def process_text(self, i, l, t):
		"""
		t is going to be a list of dictionaries
		"""
		# Read it if it's not in memory, otherwise retrieve it from the list of texts
		if not self.in_memory[i]:
			t = self.play_parser(l, open(t, 'r').read())
		else:
			t = self.play_parser(self.texts[i][0], self.texts[i][1])

		# Keep the text in memory if set. This ensures texts newly read from files are retained.
		# Otherwise just the filenames are retained, and the text is read from disk everytime.
		if self.keep_in_memory and not self.in_memory[i]:
			self.texts[i] = (l, t)
			self.in_memory[i] = True

		parsed_text = self.parse_query(t)

		if self.corpus_tokenize:
			if isinstance(parsed_text, str):
				parsed_text = self.tokenize_preprocess(i, l, parsed_text)

		return (l, parsed_text)

	def parse_query(self, t):
		if self.act != None:
			t = [i for i in [e for e in t if 'act' in e] if i['act'] in self.act]
		if self.scene != None:
			t = [i for i in [e for e in t if 'scene' in e] if i['scene'] in self.scene]
		if self.speaker!= None:
			t = [i for i in [e for e in t if 'speaker' in e] if i['speaker'] in self.speaker]

		if self.merge:
			text = [e['text'] for e in t if 'text' in e]
			text = ' '.join(text)
		else:
			# Create a list of (speaker, text) tuples
			text = [(e['speaker'], e['text']) for e in t if 'text' in e and 'speaker' in e]

		return text
