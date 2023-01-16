# -*- coding: utf-8 -*- 

import logging, re
import nltk
from collections import defaultdict

################################################################################
def ngrams(sequence, n, **kwargs):
    """
    A simple wrapper around nltk.ngrams()
    """
    return nltk.ngrams(sequence, n, **kwargs)

################################################################################
class Tokenize(object):
    """
    Tokenizes text. 

    Can be set up with custom tokenizing functions. Otherwise uses the in-built functions.
    Lowercase conversion is on by default and happens at the word_tokenize level. Word_tokenize
    can also accept regexes for tweaking the tokenizing process (without needing a separate function)

    Can also generate ngrams which don't cross sentence boundaries. e.g. "Hello, world. God save the Bean!"
    gets tokenized to [('hello', 'world'), ('god', 'save'), ('save', 'the'), ('the', 'bean')]
    """

    def __init__(self, \
            sent_tokenizer = None, \
            word_tokenizer = None, \
            keep_sentences = False, \
            ngrams = 1, \
            lowercase = True):
        self.sent_tokenizer = sent_tokenizer
        self.word_tokenizer = word_tokenizer
        self.keep_sentences = keep_sentences
        self.ngrams = ngrams
        self.lowercase = lowercase

    def tokenize(self, text):
        """
        When keep sentences is set to True, a list of lists is returned - a list of sentences, each sentence a 
        list of tokens.
        """
        tokenized = []
        sents = self.sent_tokenize(text)
        for sent in sents:
            words = self.word_tokenize(sent)
            if self.ngrams != 1:
                words = ngrams(words, self.ngrams) 
            if self.keep_sentences:
                tokenized.append(words)
            else:
                tokenized.extend(words)

        return tokenized

    def sent_tokenize(self, text):
        """
        Takes a chunk of text and tokenizes it into sentences.
        """
        # text = text.decode('utf-8')
        if self.sent_tokenizer:
            tokenized = self.sent_tokenizer(text)
        else:
            tokenized = nltk.sent_tokenize(text)

        return tokenized

    def word_tokenize(self, sent, regex = '[^\w]+'):
        """
        Takes a sentence and tokenizes it. 
        """
        if self.word_tokenizer:                 # A tokenizer has been supplied, so use it
            # Is it a function, or simply a regex
            if hasattr(self.word_tokenizer, '__call__'):
                tokenized = self.word_tokenizer(sent)
                return tokenized
            else:
                regex = self.word_tokenizer

        pattern = re.compile(regex)
        sent = pattern.sub(' ', sent)
        if self.lowercase:
            sent = sent.lower()
        tokenized = sent.split()

        return tokenized

################################################################################
class LetterNGramsTokenize(object):
    """
        @param ngram_range: The range for letter ngrams. Default is one-grams.
        @type  ngram_range: tuple of two ints (min, max)
        @param tokenizer: A function to tokenize text. 
        @type  tokenizer: function
        @param mark_boundaries: Whether or not word beginnings and endings should be marked
        @type  mark_boundaries: boolean
        @param duplicate_boundaries: Whether to count boundary ngrams twice - as part of a boundary count and by itself.
        @type  duplicate_boundaries: boolean
    """
    def __init__(self, \
            ngram_range = (1,1), \
            mark_boundaries = True, \
            duplicate_boundaries = True, \
            begin_char = '^', \
            end_char = '$', \
            tokenizer = Tokenize().tokenize
            ):
        self.ngram_range = ngram_range
        self.mark_boundaries = mark_boundaries
        self.duplicate_boundaries = duplicate_boundaries
        self.begin_char = begin_char
        self.end_char = end_char
        self.tokenizer = tokenizer

    def tokenize(self, text):
        # Tokenize if necessary
        if isinstance(text, str):
            text = self.tokenizer(text)

        lng_text = []
        for word in text:
            for ngnum in range(self.ngram_range[0], self.ngram_range[1] + 1):
                rangelen = len(word) - (ngnum - 1)
                for pos in range(0, rangelen):
                    feat = [word[pos : pos + ngnum]]
                    if self.mark_boundaries:
                        if pos == 0:
                            if self.duplicate_boundaries:
                                feat.append(self.begin_char + feat[0])
                            else:
                                feat[0] = self.begin_char + feat[0]
                        if pos == rangelen - 1:
                            if self.duplicate_boundaries:
                                feat.append(feat[0] + self.end_char)
                            else:
                                feat[0] = feat[0] + self.end_char
                    for f in feat:
                        lng_text.append(f)
        return lng_text

