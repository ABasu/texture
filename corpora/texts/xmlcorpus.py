# -*- coding: utf-8 -*- 

import logging, sys
from lxml import etree
from unidecode import unidecode
from texture.corpora.bowcorpus import BOWCorpus

################################################################################
class XMLCorpus(BOWCorpus):
	"""
	Processes XML files to extract either a plaintext corpus or a corpus of tags.
	"""
	def __init__(self, \
			*args, \
			**kwargs \
			):
		# Run the parent's init
		super(XMLCorpus, self).__init__(*args, **kwargs)

		# Set defaults for params
		self.roottag = 'TEXT'			# A default root
		self.encoding = 'utf-8'			
		self.gettags = False			# Set when we want xml tags, not texts

		self.corpus_tokenize = False

		# Make sure tokenization is turned off
		self.set_params(tokenize=False)

	def set_params(self, \
			roottag = None,
			encoding = None,
			gettags = None, 
			**kwargs):
		self.roottag = self.roottag if roottag == None else roottag
		self.encoding = self.encoding if encoding == None else encoding
		self.gettags = self.gettags if gettags == None else gettags

		# If tokenization is set, we don't pass it up to BOWCorpus but will handle it locally.
		if 'tokenize' in kwargs and kwargs['tokenize']==True:
			self.corpus_tokenize = kwargs['tokenize']
			kwargs.pop('tokenize')
		
		super(XMLCorpus, self).set_params(**kwargs)

		return self
		
	def __iter__(self):
		# Use BOWCorpus' iterator and just process the texts locally
		for i, (label, text) in enumerate(super(XMLCorpus, self).__iter__()):
			l, t = self.process_xml(i, label, text)
			yield (l, t)

	def __getitem__(self, key):
		if isinstance(key, slice):
			start = key.start if key.start else 0
			stop = key.stop if key.stop else len(self.texts)
			step = key.step if key.step else 1
			for i in range(start, stop, step):
				gen = super(XMLCorpus, self).__getitem__(i)
				l, t = list(gen)[0]
				l, t = self.process_xml(i, l, t)
				yield (l, t)
		else:
			gen = super(XMLCorpus, self).__getitem__(key)
			l, t = list(gen)[0]
			l, t = self.process_xml(key, l, t)
			yield (l,t)

	def process_xml(self, i, label, text):
		try:
			root = etree.fromstring(text)
		except etree.XMLSyntaxError:
			logging.error("Couldn't parse {}. Make sure XML is valid.".format(label))
			return (label, '')

		text = ''
		if self.gettags == False:
			text_nodes = root.xpath('//{}'.format(self.roottag))
			for text_node in text_nodes:
				textchunk = [t for t in text_node.xpath('.//text()')]
				textchunk = ' '.join(textchunk)
				text += textchunk
		else:
			tags = []
			for t in root.iter(tag=etree.Element):
				tags.append(t.tag)
			text = ' '.join(tags)

		# Do we need to get things into ascii equivalents?
		if self.encoding == 'ascii':
			text = unidecode(text)

		# Local tokenization and preprocessing
		if self.corpus_tokenize:
			text = self.tokenize_preprocess(i, label, text)

		return label, text

	def get_tags(self):
		for key, text in super(XMLCorpus, self).__iter__():
			try:
				root = etree.fromstring(text)
			except etree.XMLSyntaxError:
				logging.error("Couldn't parse {}. Make sure XML is valid.".format(key))
				continue

			tags = []
			for t in root.iter(tag=etree.Element):
				tags.append(t.tag)

			tags = ' '.join(tags)

			yield key, tags
