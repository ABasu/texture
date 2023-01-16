#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import sys, os
from lxml import etree
import texture as txt

cp = txt.corpora.texts.xmlcorpus.XMLCorpus(encoding='ascii').fit("/Users/anupam/Desktop/Corpora/eebo_tcp/xml_tidy/A12777.xml")

for t in cp.get_tags():
	print(t)
