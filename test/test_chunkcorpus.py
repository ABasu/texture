# -*- coding: utf-8 -*- 

import unittest
import texture as txt

class BOWCorpusTest(unittest.TestCase):

	def __init__(self, *args, **kwargs):
		# Make sure we're not overwriting TestCase's init
		super(BOWCorpusTest, self).__init__(*args, **kwargs)

		# Some sample input
		self.texts = [('first.txt', "Shall I compare thee to a summer's day?"), \
				 ('second.txt', "Thou art more lovely and more temperate."), \
				 ('third.txt', "Rough winds do shake the darling buds of May,"), \
				 ('fourth.txt', "And summer's lease hath all too short a date.")]
		self.path = "./data/txt_files/*.txt"

	def test_iter(self):
		cp = txt.corpora.texts.chunkcorpus.ChunkCorpus().fit(self.texts)
		cp.set_params(chunksize=4)
		for i, (l, c) in enumerate(cp):
			if i==0:
				self.assertEqual(c, self.texts[0][1].lower().strip().split()[:4])
	
	def test_getitem(self):
		cp = txt.corpora.texts.chunkcorpus.ChunkCorpus().fit(self.texts)
		cp.set_params(chunksize=4)
		self.assertEqual(cp[0][0][1], self.texts[0][1].lower().strip().split()[:4])
	
if __name__ == '__main__':
	unittest.main()


