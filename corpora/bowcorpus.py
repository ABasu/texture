# -*- coding: utf-8 -*-

from io import open
import glob, os, re, random, logging, sys
from gensim import corpora

import texture as txt
from texture.nlp.tokenize import Tokenize

################################################################################
class BOWCorpus(object):
    """
    A base class for bag-of-words corpora. This class will be inherited by all
    corpus classes designed to ingest text.

    This class implements 5 custom parameters.

    1. tokenize: A flag that turns tokenization on or off
    2. tokenizer: A custom tokenization function that takes a string and returns a tokenized list.
    3. stopwords: A list of words to be eliminated. Works only when tokenization is on.
    4. gowords: A list of words to retain. Works only when tokenization is on.
    5. keep_in_memory: Retain (label, text) pairs once they've been read.
    """

    def __init__(self):
        """
        Initializes the Corpus object and sets default attributes.
        """
        # Internal attributes
        # Keep track of texts and filenames
        self.texts = None
        self.filenames = False
        # Keep track of in memory states of texts
        self.in_memory = False
        self.tokenized = False

        # Set defaults for params
        self.tokenize = None
        self.tokenizer = Tokenize().tokenize
        self.stopwords = None
        self.gowords = None
        self.keep_in_memory = False

    def fit(self, \
            texts, \
            filenames = False, \
            ):
        """
        Loads data into the corpus. Expects one of the following:
            - Label / Filename pairs (set filenames=True)
            - Label / Text pairs.
            - A generator that produces Label / Text pairs and is iterable and indexable

        Note: Label / Text pairs are just a special case of such a generator.

        As a convenience, we'll accept the following variations to the (label, filename) option.
            - Just a path with wildcards - this will be expanded with glob and treated as below - as a
            list of filenames.
            - A list of filenames. Labels will be generated as the filenames without the directory. A
            warning will suggest that the filenames=True flag should ideally be set.

        @param texts: This can be one of several things:
            - A list of (label, filename) pairs. C{filenames} needs to be set to C{True}.
                - Two variations of this are acceptable.
                    - A single string with wildcards.
                    - A list of string filenames.
            - A C{list of (label, text) tuples}
                - A dictionary in {label: text} form is also acceptable and will be converted.
                - text can be either a single string or a list of tokens.
            - A generator for (label, string) pairs, that implements len, indexing, and iteration.
        @type  texts: string, list of strings, list of tuples
        @param files: Denotes whether the string is to be treated as a filename to be read. Default: C{False}
        @type  files: boolean
        """
        # If we've received a dictionary, convert to list of tuples
        if isinstance(texts, dict):
            texts = [(k, texts[k]) for k in texts]

        # Check if empty list or empty string
        if len(texts) == 0:
            logging.error('Received an empty text-list, check path')
            sys.exit()

        # If filenames is set we expect a list of (label, filename) tuples. But we will also accept the following
        # with a warning:
        #    * A single string to be globbed, then treated as below
        #    * A list of filenames (labels will be generated from them by stripping off directory and extension)
        if (isinstance(texts, str) or (isinstance(texts, list) and isinstance(texts[0], str))) and filenames == False:
            logging.warning('Assuming that strings are filenames. It is recommended that filenames=True be set')
            filenames = True

        # If we have received filenames, set self.filenames to True, convert into (label, filename)
        # tuples, and set in_memory and tokenized to False lists
        if filenames:
            self.filenames = True
            # Glob if needed
            if isinstance(texts, str):
                texts = glob.glob(texts)
            # Generate labels from filenames if needed
            if not isinstance(texts[0], tuple):
                texts = [(os.path.split(f)[1],f) for f in texts]
            self.in_memory = [False] * len(texts)
            self.tokenized = [False] * len(texts)
            self.n_tokens = [None] * len(texts)
        # We have either received a list of tuples, or some other (label, text) generator
        # We can assume texts are in memory (the generator can handle them differently behind the scenes
        # but for our purposes they look like they are in memory).
        # We also set tokenized to None for all texts. We'll generate true / false values the first time we
        # encounter them
        else:
            # We trust the generator to give us texts in the proper format, but for a list we
            # check if the first item is a tuple.
            if isinstance(texts, list):
                if not isinstance(texts[0], tuple):
                    logging.error("Expecting a list of tuples, check datatype for texts")
                    sys.exit()
            self.in_memory = [True] * len(texts)
            self.tokenized = [None] * len(texts)
            self.n_tokens = [None] * len(texts)

        # At this point self.texts will have one of the following cases
        # 1. It'll be a list of (label, filename) tuples with:
        #        - self.filenames set to True
        #        - self.in_memory set to Falses
        #        - self.tokenized set to Falses
        # 2. It'll be a list of (label, text) tuples.
        #        - self.filenames set to false
        #        - self.in_memory set to Trues
        #        - self.tokenized set to Nones since we don't know for all texts. It'll be set the first time
        #            we access a text.
        # 3. It'll be a generator of (label, text) tuples
        #        - self.filenames set to false
        #        - self.in_memory set to trues (the generator can handle it any way it wants)
        #        - self.tokenized set to Nones since we don't know for all texts. It'll be set the first time
        #            we access a text.
        self.texts = texts

        logging.info('Fit {} texts to the corpus'.format(len(texts)))

        return self

    def set_params(self, \
            tokenize = None, \
            tokenizer = None, \
            stopwords = None, \
            gowords = None, \
            keep_in_memory=None):
        """
        Sets tokenization on and off. Can assign custom tokenizer and stop and go words lists.

        Sets the keep_in_memory flag. Once this is set, a text will be read from disk only the first time
        and then stored in memory. ALL of the corpus must fit into RAM to use this flag!
        """
        # We retain the default if the value hasn't been supplied, else we change it
        self.tokenize = self.tokenize if tokenize == None else tokenize

        self.tokenizer = self.tokenizer if tokenizer == None else tokenizer
        self.stopwords = self.stopwords if stopwords == None else stopwords
        self.gowords = self.gowords if gowords == None else gowords

        self.keep_in_memory = self.keep_in_memory if keep_in_memory == None else keep_in_memory

        return self

    def __iter__(self):
        """
        Iter through the list of texts.
        """
        for i, (l, t) in enumerate(self.texts):
            l, t = self.process_text(i, l, t)
            yield (l, t)

    def __getitem__(self, key):
        if isinstance(key, slice):
            start = key.start if key.start else 0
            stop = key.stop if key.stop else len(self.texts)
            step = key.step if key.step else 1
            for i in range(start, stop, step):
                l, t = self.texts[i]
                l, t = self.process_text(i, l, t)
                yield (l, t)
        else:
            l, t = self.texts[key]
            l, t = self.process_text(key, l, t)
            yield (l,t)

    def __len__(self):
        return len(self.texts)

    def __str__(self):
        """
        Prints a string representation
        """
        s = ("No. of texts: {}\n"
            "Tokenize: {}\n"
            "Keep in Memory: {}\n\n").format(len(self.texts), self.tokenize, self.keep_in_memory)
        if len(self.texts) > 40:
            for i, (l, t) in enumerate(self.texts[:20]):
                s += "{:>6}) {:20.18}: {:100.100}\n".format(i, l, t)
            s += "...\n"
            for i, (l, t) in enumerate(self.texts[-20:]):
                s += "{:>6}) {:20.18}: {:100.100}\n".format(len(self.texts)-i, l, t)
        else:
            for i, (l, t) in enumerate(self.texts):
                s += "{:>6}) {:20.18}: {:100.100}\n".format(i, l, t)

        return s

    def process_text(self, i, l, t):
        """
        Processes a text item according to set class attributes. Reads it if it's a file.
        Processes it and returns (label, text).
        """
        # If we only have filenames, read the text from the file
        if self.filenames:
            t = open(t, 'r', encoding='utf-8', errors='ignore').read()

        # Deduce whether the text is tokenized the first time we encounter it
        if self.tokenized[i] == None:
            if isinstance(t, list):
                self.tokenized[i] = True
                self.n_tokens[i] = len(t)
            else:
                self.tokenized[i] = False

        # Tokenize if necessary
        if self.tokenize == True:
            t = self.tokenize_preprocess(i, l, t)
        # if self.tokenized is unset, keep texts in original form
        elif self.tokenize == None:
            pass
        # Tokenize is false, but we have tokens - so join them
        else:
            if self.tokenized[i]:
                t = ' '.join(t)

        # Keep the text in memory if set. This ensures texts newly read from files are retained.
        # Otherwise just the filenames are retained, and the text is read from disk everytime.
        if self.keep_in_memory and not self.in_memory[i]:
            self.texts[i] = (l, t)
            self.in_memory[i] = True

        return (l, t)

    def tokenize_preprocess(self, i, l, t):
        """
        If the text is not tokenized, tokenize it, then preprocess and filter using
        stop and go lists.
        """
        if not self.tokenized[i]:
            t = self.tokenizer(t)
            self.n_tokens[i] = len(t)
        # for tokenized text we can implement stop and go words
        if self.stopwords:
            t = [w for w in t if w not in self.stopwords]
        if self.gowords:
            t = [w for w in t if w in self.gowords]

        return t

    def get_labels(self):
        """
        Generates a list of labels.
        """
        return [l for l,t in self.texts]

    def get_gensim_dictionary(self):
        """
        Generates a gensim dictionary object. See U{https://radimrehurek.com/gensim/corpora/dictionary.html}
        """
        return corpora.Dictionary((t for l, t in self))

    def get_gensim_dictionary_corpus(self, dictionary=None):
        """
        Generates a gensim dictionary and corpus objects. Can accept a gensim dictionary if we want to limit
        the corpus to a specific field of tokens.

        For example, to find tfidf scores for only a small set of texts against the entirety of a corpus, we
        can train on a dictionary based on the subset.
        """
        dictionary = self.get_gensim_dictionary() if dictionary==None else dictionary
        corpus = [dictionary.doc2bow(t) for l, t in self]
        return dictionary, corpus
