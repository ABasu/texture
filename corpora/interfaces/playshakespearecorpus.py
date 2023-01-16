# -*- coding: utf-8 -*- 

import logging, os
from lxml import etree

################################################################################

def playshakespeare_parse(l, t):
	"""
	This function takes a label and the raw xml from the PlayShakespeare.com corpus
	and returns a list of dictionaries. It is designed to be used as a parse_play 
	interface to the Drama corpus.
	"""
	root = etree.fromstring(t)
	if (root.xpath('//play/text()') == []):
		logging.error('Ignoring %s. Not a properly formatted play.' % l)
		return (l, '')

	t = []
	# Parse the characters
	for character in root.xpath('//personae/persona'):
		name = character.xpath('./persname/text()')[0]
		gender = character.xpath('@gender')[0]
		short = character.xpath('./persname/@short')[0]
		t.append({'type':'character', 'name':name, 'gender':gender, 'short':short})

	for a, act in enumerate(root.xpath('//act')):
		for s, scene in enumerate(act.xpath('./scene')):
			try:
				location = scene.xpath('./scenelocation/text()')[0]
			except:
				location = "None"
			t.append({'type':'location', 'act':a+1, 'scene':s+1, 'text':location})
			for scene_element in scene.xpath('./stagedir | ./speech'):
				if scene_element.tag == 'stagedir':
					text = scene_element.xpath('./text()')[0]
					t.append({'type': 'stagedir', 'act':a+1, 'scene':s+1, 'text':text})
				elif scene_element.tag == 'speech':
					try:
						speaker = scene_element.xpath('./speaker/text()')[0]
					except:
						speaker = "None"
					text = ' '.join(scene_element.xpath('./line/text()'))
					t.append({'type': 'speech', 'act':a+1, 'scene':s+1, 'speaker': speaker, 'text': text})

	return t

