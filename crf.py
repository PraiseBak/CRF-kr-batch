#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Laon-CRF
	: Easy-to-use Linear Chain Conditional Random Fields

Author: Seong-Jin Kim
License: MIT License
Version: 0.0
Email: lancifollia@gmail.com
Created: May 13, 2015

Copyright (c) 2015 Seong-Jin Kim
"""


from read_corpus import read_conll_corpus
from feature import FeatureSet, STARTING_LABEL_INDEX

from math import exp, log
import numpy as np
from scipy.optimize import fmin_l_bfgs_b

import time
import json
import datetime
import sys
from collections import Counter
from nltk.tokenize import syllable_tokenize, word_tokenize
import CRF_batch
import CRF_lib

SCALING_THRESHOLD = 1e250

ITERATION_NUM = 0
SUB_ITERATION_NUM = 0
TOTAL_SUB_ITERATIONS = 0
GRADIENT = None


def _callback(params):
	global ITERATION_NUM
	global SUB_ITERATION_NUM
	global TOTAL_SUB_ITERATIONS
	ITERATION_NUM += 1
	TOTAL_SUB_ITERATIONS += SUB_ITERATION_NUM
	SUB_ITERATION_NUM = 0

def _generate_potential_table(params, num_labels, feature_set, X, inference=True):
	"""
	Generates a potential table using given observations.
	* potential_table[t][prev_y, y]
		:= exp(inner_product(params, feature_vector(prev_y, y, X, t)))
		(where 0 <= t < len(X))
	"""
	tables = list()
	for t in range(len(X)):
		table = np.zeros((num_labels, num_labels))
		if inference:
			#테스트용
			#이전 y ,
			for (prev_y, y), score in feature_set.calc_inner_products(params, X, t):
				if prev_y == -1:
					table[:, y] += score
				else:
					table[prev_y, y] += score

		else:
			#학습용
			#어절단위로 각 어절에서 생성된 feature를
			for (prev_y, y), feature_ids in X[t]:
				score = sum(params[fid] for fid in feature_ids)
				if prev_y == -1:
					table[:, y] += score
				else:
					table[prev_y, y] += score

		#지수함수로 변환
		table = np.exp(table)
		if t == 0:

			table[STARTING_LABEL_INDEX+1:] = 0

		else:
			# 자기 자신의 가중치는 0으로 두는 부분인것같음
			# 모든행의 STARTING_LABEL_INDEX 번째 값 0
			table[:,STARTING_LABEL_INDEX] = 0
			# STARTING_LABEL_INDEX 행의 모든 값 0
			table[STARTING_LABEL_INDEX,:] = 0
		tables.append(table)
	return tables


def _forward_backward(num_labels, time_length, potential_table):
	"""
	Calculates alpha(forward terms), beta(backward terms), and Z(instance-specific normalization factor)
		with a scaling method(suggested by Rabiner, 1989).
	* Reference:
		- 1989, Lawrence R. Rabiner, A Tutorial on Hidden Markov Models and Selected Applications
		in Speech Recognition
	"""
	alpha = np.zeros((time_length, num_labels))
	scaling_dic = dict()
	t = 0
	for label_id in range(num_labels):
		alpha[t, label_id] = potential_table[t][STARTING_LABEL_INDEX, label_id]
	#alpha[0, :] = potential_table[0][STARTING_LABEL_INDEX, :]  # slow
	t = 1
	while t < time_length:
		scaling_time = None
		scaling_coefficient = None
		overflow_occured = False
		label_id = 1
		while label_id < num_labels:
			alpha[t, label_id] = np.dot(alpha[t-1,:], potential_table[t][:,label_id])
			if alpha[t, label_id] > SCALING_THRESHOLD:
				if overflow_occured:
					print('******** Consecutive overflow ********')
					raise BaseException()
				overflow_occured = True
				scaling_time = t - 1
				scaling_coefficient = SCALING_THRESHOLD
				scaling_dic[scaling_time] = scaling_coefficient
				break
			else:
				label_id += 1
		if overflow_occured:
			alpha[t-1] /= scaling_coefficient
			alpha[t] = 0
		else:
			t += 1

	beta = np.zeros((time_length, num_labels))
	t = time_length - 1
	for label_id in range(num_labels):
		beta[t, label_id] = 1.0
	#beta[time_length - 1, :] = 1.0	 # slow
	for t in range(time_length-2, -1,-1):
		for label_id in range(1, num_labels):
			beta[t,label_id] = np.dot(beta[t+1,:],potential_table[t+1][label_id,:])
		if t in scaling_dic.keys():
			beta[t] /= scaling_dic[t]
	Z = sum(alpha[time_length-1])
	return alpha, beta, Z, scaling_dic


def _calc_path_score(potential_table, scaling_dic, Y, label_dic):
	score = 1.0
	prev_y = STARTING_LABEL_INDEX
	for t in range(len(Y)):
		y = label_dic[Y[t]]
		score *= potential_table[prev_y, y, t]
		if t in scaling_dic.keys():
			score = score / scaling_dic[t]
		prev_y = y


def _log_likelihood(params, *args):
	"""
	Calculate likelihood and gradient
	"""
	training_data, feature_set, training_feature_data, empirical_counts, label_dic, squared_sigma = args
	expected_counts = np.zeros(len(feature_set))

	total_logZ = 0

	i = 0
	import time
	for X_features in training_feature_data:
		potential_table = _generate_potential_table(params, len(label_dic), feature_set,
													X_features, inference=False)

		i += 1
		alpha, beta, Z, scaling_dic = _forward_backward(len(label_dic), len(X_features), potential_table)
		total_logZ += log(Z) + \
					  sum(log(scaling_coefficient) for _, scaling_coefficient in scaling_dic.items())

		for t in range(len(X_features)): # 어절 loop
			potential = potential_table[t]
			for (prev_y, y), feature_ids in X_features[t]:
				# Adds p(prev_y, y | X, t)
				# print (prev_y)
				# print (y)
				if prev_y == -1:
					if t in scaling_dic.keys():
						prob = (alpha[t, y] * beta[t, y] * scaling_dic[t])/Z
					else:
						prob = (alpha[t, y] * beta[t, y])/Z
				elif t == 0:
					if prev_y is not STARTING_LABEL_INDEX:
						continue
					else:
						prob = (potential[STARTING_LABEL_INDEX, y] * beta[t, y])/Z
				else:
					if prev_y is STARTING_LABEL_INDEX or y is STARTING_LABEL_INDEX:
						continue
					else:
						prob = (alpha[t-1, prev_y] * potential[prev_y, y] * beta[t, y]) / Z
				for fid in feature_ids:
					expected_counts[fid] += prob
					if prob < 0:
						print(prob)
	likelihood = np.dot(empirical_counts, params) - total_logZ - \
				 np.sum(np.dot(params,params))/(squared_sigma*2)
	gradients = empirical_counts - expected_counts - params/squared_sigma

	global GRADIENT
	GRADIENT = gradients

	
	global SUB_ITERATION_NUM
	sub_iteration_str = '	'
	if SUB_ITERATION_NUM > 0:
		sub_iteration_str = '(' + '{0:02d}'.format(SUB_ITERATION_NUM) + ')'
	print('  ', '{0:03d}'.format(ITERATION_NUM), sub_iteration_str, ':', likelihood * -1)

	SUB_ITERATION_NUM += 1
	return likelihood * -1


def _gradient(params, *args):
	return GRADIENT * -1


class LinearChainCRF():
	"""
	Linear-chain Conditional Random Field
	"""

	training_data = None
	feature_set = None

	label_dic = None
	label_array = None
	num_labels = None

	params = None

	# For L-BFGS
	squared_sigma = 10.0

	def __init__(self):
		pass

	def _read_corpus(self, filename):
		return read_conll_corpus(filename)

	def _get_training_feature_data(self):
		return [[self.feature_set.get_feature_list(X, t) for t in range(len(X))]
				for X, _ in self.training_data]

	def _estimate_parameters(self):
		"""
		Estimates parameters using L-BFGS.
		* References:
			- R. H. Byrd, P. Lu and J. Nocedal. A Limited Memory Algorithm for Bound Constrained Optimization,
			(1995), SIAM Journal on Scientific and Statistical Computing, 16, 5, pp. 1190-1208.
			- C. Zhu, R. H. Byrd and J. Nocedal. L-BFGS-B: Algorithm 778: L-BFGS-B, FORTRAN routines for large
			scale bound constrained optimization (1997), ACM Transactions on Mathematical Software, 23, 4,
			pp. 550 - 560.
			- J.L. Morales and J. Nocedal. L-BFGS-B: Remark on Algorithm 778: L-BFGS-B, FORTRAN routines for
			large scale bound constrained optimization (2011), ACM Transactions on Mathematical Software, 38, 1.
		"""
		# 학습전 피쳐
		'''
			scale bound constrained optimization (1997), ACM Transactions on Mathematical Software, 23, 4,
			scale bound constrained optimization (1997), ACM Transactions on Mathematical Software, 23, 4,
			pp. 550 - 560.
			- J.L. Morales and J. Nocedal. L-BFGS-B: Remark on Algorithm 778: L-BFGS-B, FORTRAN routines for
			large scale bound constrained optimization (2011), ACM Transactions on Mathematical Software, 38, 1.
		# 학습전 피쳐
		'''
		stopwatch('before get features')	
		training_feature_data = self._get_training_feature_data()
		stopwatch('after get features') 
		# 학습후피쳐

		print('* Squared sigma:', self.squared_sigma)
		print('* Start L-BGFS')
		print('   ========================')
		print('   iter(sit): likelihood')
		print('   ------------------------')
		iteration_start = time.time()
		self.params, log_likelihood, information = \
				fmin_l_bfgs_b(func=_log_likelihood, fprime=_gradient,
							  x0=np.zeros(len(self.feature_set)),
							  args=(self.training_data, self.feature_set, training_feature_data,
									self.feature_set.get_empirical_counts(),
									self.label_dic, self.squared_sigma),
							  maxiter=100,
							  
							  callback=_callback)
		print('   ========================')
		print('   (iter: iteration, sit: sub iteration)')
		print('* Training has been finished with %d iterations' % information['nit'])
		print("iteration ended time =",time.time() - iteration_start)

		if information['warnflag'] != 0:
			print('* Warning (code: %d)' % information['warnflag'])
			if 'task' in information.keys():
				print('* Reason: %s' % (information['task']))
		print('* Likelihood: %s' % str(log_likelihood))

		

	def train(self, corpus_filename, model_filename,batch):
		"""
		Estimates parameters using conjugate gradient methods.(L-BFGS-B used)
		"""
		start_time = time.time()
		print('[%s] Start training' % datetime.datetime.now())

		# Read the training corpus
		print("* Reading training data ...\n ")
		
		if batch == False or batch == None:
			batch = 1
		CRF_bat = CRF_batch.CRFBatch(corpus_filename,batch)
		print('Read training data complete')

		# Generate feature set from the corpus

		feature_time_start = time.time()

		for iter in range(batch):
			if batch == 1:
				self.training_data = self._read_corpus(corpus_filename)
			else:
				self.training_data = CRF_bat.return_corpus()
			
			self.feature_set = FeatureSet()
			self.feature_set.scan(self.training_data)
			self.label_dic, self.label_array = self.feature_set.get_labels()
			self.num_labels = len(self.label_array)
		
			print("feature 생성 걸린 시간 = ",time.time() - feature_time_start)

			print("* Number of labels: %d" % (self.num_labels-1))
			print("* Number of features: %d" % len(self.feature_set))

			# Estimates parameters to maximize log-likelihood of the corpus.
			self._estimate_parameters()
			self.save_model(model_filename)

			elapsed_time = time.time() - start_time
			print('*총 소요 시간 Elapsed time: %f' % elapsed_time)
			print('* [%s] Training done' % datetime.datetime.now())



	def check_filename(self,filename):
		import os
		if not os.path.exists(filename):
			return filename
		else:
			count = 0
			origin_filename = filename
			while True:
				tmp_filename = origin_filename.split('.')
				filename = tmp_filename[0] + str(count) +'.'+ tmp_filename[1]
				if not os.path.exists(filename):
					return filename
				count += 1


	def write_result(self,Y_list,filename):

		output_file = filename.split('.')[0]+'.result'
		output_file = self.check_filename(filename.split('.')[0]+'.result')
		with open(output_file,'w') as f:
			for line in Y_list:
				if line != '\n':
					f.write(line+'\n')
		print('result prediction file:',output_file)
	
	#CRF.inference_sentense("문장입니다.",model_filename,False)
	def inference_sentense(self, sentense,model):
		self.load(model)
		if self.params is None:
			raise BaseException("You should load a model first!")
		start_time = time.time()
		emjeol_list = list()
		emjeol_list = syllable_tokenize(sentense,"korean") 
		print("코퍼스  읽는데 걸린 시간 =",time.time() - start_time)
		Y_list = list()

		for X in emjeol_list:
			Yprime = self.inference(X)
			for i in range(len(Yprime)):
				Y_list.append((X[i],Yprime[i]))
				#Y_list.append(X[i] + '\t' +Yprime[i])
		print(Y_list)
		#self.write_result(Y_list,model)



	def only_inference(self, test_corpus_filename,model,batch):
		self.load(model)
		if self.params is None:
			raise BaseException("You should load a model first!")
		start_time = time.time()
		emjeol_list = list()
		emjeol_list = self.file_to_emjeol(test_corpus_filename)
		print("코퍼스  읽는데 걸린 시간 =",time.time() - start_time)
		#마킹 + 음절+ 예측한 형태소
		Y_list = list()
		for i in range(len(emjeol_list)):
			for X in emjeol_list[i]:
				Yprime = self.inference(X)
				for j in range(len(Yprime)):
					is_first = 0
					if j == 0:
						is_first = 1
					Y_list.append(str(is_first) + '\t' + X[j] + '\t' +Yprime[j])
		#마킹기반 어절 + 예측한 형태소
		word_Y = emjeol_to_word(Y_list)
		#model파일이름.result에 저장
		self.write_result(word_Y,model)
			


	def print_test_result(self, test_corpus_filename):
		test_data = self._read_corpus(test_corpus_filename)

		for X, Y in test_data:
			Yprime = self.inference(X)
			for t in range(len(X)):
				print('%s\t%s\t%s' % ('\t'.join(X[t]), Y[t], Yprime[t]))
			print()

	def inference(self, X):
		"""
		Finds the best label sequence.
		"""
		generate_table_start = time.time()
		potential_table = _generate_potential_table(self.params, self.num_labels,
													self.feature_set, X, inference=True)
		#print("추론 테이블 생성에 걸린 시간",time.time() -  generate_table_start)
		#print(potential_table)
		viterbi_start = time.time()
		Yprime = self.viterbi(X, potential_table)
		#print("viterbi 걸린 시간=",time.time() - viterbi_start)
		return Yprime


	def viterbi(self, X, potential_table):
		"""
		The Viterbi algorithm with backpointers
		"""
		time_length = len(X)
		max_table = np.zeros((time_length, self.num_labels))
		argmax_table = np.zeros((time_length, self.num_labels), dtype='int64')

		t = 0
		for label_id in range(self.num_labels):
			max_table[t, label_id] = potential_table[t][STARTING_LABEL_INDEX, label_id]
		for t in range(1, time_length):
			for label_id in range(1, self.num_labels):
				max_value = -float('inf')
				max_label_id = None
				for prev_label_id in range(1, self.num_labels):
					value = max_table[t-1, prev_label_id] * potential_table[t][prev_label_id, label_id]
					if value > max_value:
						max_value = value
						max_label_id = prev_label_id
				max_table[t, label_id] = max_value
				argmax_table[t, label_id] = max_label_id

		sequence = list()
		next_label = max_table[time_length-1].argmax()
		sequence.append(next_label)
		for t in range(time_length-1, -1, -1):
			next_label = argmax_table[t, next_label]
			sequence.append(next_label)
		return [self.label_dic[label_id] for label_id in sequence[::-1][1:]]

	def save_model(self, model_filename):
		model = {"feature_dic": self.feature_set.serialize_feature_dic(),
				 "num_features": self.feature_set.num_features,
				 "labels": self.feature_set.label_array,
				 "params": list(self.params)}
		f = open(model_filename, 'w')
		json.dump(model, f, ensure_ascii=False, indent=2, separators=(',', ':'))
		f.close()
		import os
		print('* Trained CRF Model has been saved at "%s/%s"' % (os.getcwd(), model_filename))
		

	def load(self, model_filename):
		f = open(model_filename)
		model = json.load(f)
		f.close()
		self.feature_set = FeatureSet()
		self.feature_set.load(model['feature_dic'], model['num_features'], model['labels'])
		self.label_dic, self.label_array = self.feature_set.get_labels()
		self.num_labels = len(self.label_array)
		self.params = np.asarray(model['params'])
		print('CRF model loaded')

	
	def file_to_emjeol(self,filename):
		content = return_file_content(filename)
		word = return_word(content)
		emjeol_list = return_emjeol(word)
		return emjeol_list

# For testing
#crf = LinearChainCRF()

#crf.train('data/chunking/simple_train.data', 'data/chunking/model_5.json')
#crf.load('data/chunking/model_5.json')
#crf.test('data/chunking/simple_test.data')

#crf.train('data/chunking_2/train.txt', 'data/chunking_2/model_4.json')
#crf.load('data/chunking_2/model_4.json')
#crf.test('data/chunking_2/test.txt')


def emjeol_to_word(Y):
	word_Y = list()
	word_str = ""
	morph_str = ""	
	
	for y in Y:
		element = y.split('\t')
		is_first = element[0]
		if is_first == '1':
			word_Y.append(word_str + '\t' + morph_str.rstrip('+'))
			word_str = ""
			morph_str = ""
		word_str += element[1]
		morph_str += element[1]+'/'+element[2] +'+'
	word_Y.append(word_str + '\t' + morph_str.rstrip('+'))
	word_Y.pop(0)	
	return word_Y

def return_file_content(filename):
	with open(filename,'r',encoding='cp949') as f:
		return f.readlines()


def return_word(content):
	word_list = list()
	for line in content:
		word_list.append(word_tokenize(line,'korean'))
	return word_list


def return_emjeol(word_list):
	emjeol_list = list()
	for word in word_list:
		emjeol_list.append(syllable_tokenize(word,'korean'))
	return emjeol_list





def batch_testcode():
	CRF = LinearChainCRF()

	input_filename = "mini_Sejong.txt"
	model_name = "test_batch.model"
	batch = 4
	CRF.train(input_filename,model_name,batch)


if __name__ == "__main__":
	batch_testcode()
