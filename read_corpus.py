#!/usr/bin/env python
# -*- coding: utf-8 -*-


def read_file_batch_ver(file,batch_unit):
	data = list()
	element_size = 0
	X = list()
	Y = list()

	for i in range(0,batch_unit):
		data_line = file.readline()
		words = data_line.strip().split()
		
		if len(words) is 0:
			data.append((X, Y))
			X = list()
			Y = list()
			#끝이니까
			print(data_line)
			return data
		else:
			if element_size is 0:
				element_size = len(words)
			elif element_size is not len(words):
				raise FileFormatError
			X.append(words[:-1])
			Y.append(words[-1])
	data.append((X,Y))	
	if len(X) > 0:
		data.append((X, Y))
	print(data_line)
	return data


def read_conll_corpus(filename):
	"""
	Read a corpus file with a format used in CoNLL.
	"""
	data = list()
	data_string_list = list(open(filename,'r',encoding="utf-8"))
	element_size = 0
	X = list()
	Y = list()
	import sys
		
	for data_string in data_string_list:
		
		words = data_string.strip().split()
		if len(words) is 0:
			data.append((X, Y))
			X = list()
			Y = list()
		else:
			if element_size is 0:
				element_size = len(words)
			elif element_size is not len(words):
				print('err')
				exit()
			X.append(words[:-1])
			Y.append(words[-1])
		
	if len(X) > 0:
		data.append((X, Y))
	return data
