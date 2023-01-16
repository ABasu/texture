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
	
	def test_fit_list(self):
		# Test that we can load a list of tuples
		cp = txt.corpora.bowcorpus.BOWCorpus().fit(self.texts)
		self.assertEqual(cp.texts, self.texts)

	def test_fit_glob(self):
		# Test that we can load from files
		cp = txt.corpora.bowcorpus.BOWCorpus().fit(self.path, filenames=True)
		# Since we are reading files, we need to find out the order.
		order = {}
		for i, (l, t) in enumerate(self.texts):
			for i1, (l1, t1) in enumerate(cp.texts):
				if l == l1:
					order[i] = i1
		# Test the label and the text match (after stripping any newlines from the file
		self.assertEqual(cp[order[1]][0], self.texts[1][0])
		self.assertEqual(cp[order[1]][1].strip(), self.texts[1][1])

	def test_fit_corpus(self):
		# test that we can load another corpus
		cp = txt.corpora.bowcorpus.BOWCorpus().fit(self.path, filenames=True)
		# Since we are reading files, we need to find out the order.
		order = {}
		for i, (l, t) in enumerate(self.texts):
			for i1, (l1, t1) in enumerate(cp.texts):
				if l == l1:
					order[i] = i1
		cp1 = txt.corpora.bowcorpus.BOWCorpus().fit(cp)
		cp1.set_params(tokenize=True)
		self.assertListEqual(cp1[order[2]][1], ['rough', 'winds', 'do', 'shake', 'the', 'darling', 'buds', 'of', 'may'])

	def test_set_tokenize(self):
		# test that tokenization works
		cp = txt.corpora.bowcorpus.BOWCorpus().fit(self.texts)
		cp.set_params(tokenize=True)
		self.assertListEqual(cp[2][1], ['rough', 'winds', 'do', 'shake', 'the', 'darling', 'buds', 'of', 'may'])
		cp.set_params(tokenize=False)
		self.assertEqual(cp[2][1], self.texts[2][1])
		
	def test_keep_in_memory(self):
		cp = txt.corpora.bowcorpus.BOWCorpus().fit(self.path, filenames=True)
		cp.set_params(tokenize=True, keep_in_memory=True)
		# Since we are reading files, we need to find out the order.
		order = {}
		for i, (l, t) in enumerate(self.texts):
			for i1, (l1, t1) in enumerate(cp.texts):
				if l == l1:
					order[i] = i1
		self.assertListEqual(cp[order[2]][1], ['rough', 'winds', 'do', 'shake', 'the', 'darling', 'buds', 'of', 'may'])

	def test_iter(self):
		cp = txt.corpora.bowcorpus.BOWCorpus().fit(self.texts)
		for i, (l, t) in enumerate(cp):
			self.assertEqual(l, self.texts[i][0])
			self.assertEqual(t, self.texts[i][1])

	def test_getitem(self):
		cp = txt.corpora.bowcorpus.BOWCorpus().fit(self.texts)
		self.assertEqual(cp[1], self.texts[1])
		self.assertEqual(cp[1:3], self.texts[1:3])
		self.assertEqual(cp[0:4:2], self.texts[0:4:2])

if __name__ == '__main__':
	unittest.main()

