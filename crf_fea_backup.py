# -*- coding: utf-8 -*-
import make_eumjeol_corpus as make_eumjeol


def return_corpus(filename):
	output_filename = make_eumjeol.start(filename)
	return output_filename

def return_corpus_data(filename):
	corpus_filename = return_corpus(filename)
	#corpus_filename is eumjeol converted file
	#need dict convert
	import read_corpus
	result = read_corpus.read_conll_corpus(corpus_filename)
	return result
