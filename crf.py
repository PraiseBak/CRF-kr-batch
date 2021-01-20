#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Laon-CRF
	: Easy-to7-use Linear Chain Conditional Random Fields

Author: Seong-Jin Kim
License: MIT License
Version: 0.0
Email: lancifollia@gmail.com
Created: May 13, 2015

Copyright (c) 2015 Seong-Jin Kim



modify by ChanYang Park 2021
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
from nltk.metrics import accuracy
import utils
import CRF_batch


SCALING_THRESHOLD = 1e250
ITERATION_NUM = 0
SUB_ITERATION_NUM = 0
TOTAL_SUB_ITERATIONS = 0
GRADIENT = None
is_batch = False
train_data = None


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
	#X = 한문장
	for t in range(len(X)):
		#레이블 개수 x 레이블개수 행렬 생성

		table = np.zeros((num_labels, num_labels))
		if inference:
			for (prev_y, y), score in feature_set.calc_inner_products(params, X, t):

				if prev_y == -1:
					table[:, y] += score
				else:
					table[prev_y, y] += score

		else:
			#t번째 음절을 넣었을 때 나오는 feature_id에 해당하는  가중치를 모두 더해서
			#테이블의 prev_y,y 이나 -1,y면 전체,y에 넣는다
			for (prev_y, y), feature_ids in X[t]:
				score = sum(params[fid] for fid in feature_ids)
				if prev_y == -1:
					table[:, y] += score
				else:
					table[prev_y, y] += score
		#한 음절마다
		table = np.exp(table)
			
		if t == 0:
			table[STARTING_LABEL_INDEX+1:] = 0
		else:
			table[:,STARTING_LABEL_INDEX] = 0
			table[STARTING_LABEL_INDEX,:] = 0

		tables.append(table)
	#tables는 tables[t번째][확률테이블] 확률 테이블은[prev_y,y] = 확률값 (그 음절이 나왔을때 생성된 모든 피쳐의 가중치더해진)
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
			#현재 레이블이면서 현재 음절이 될 확률 = 이전 음절 나올 확률 * 현재 레이블일 확률 *
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
			#현재 음절이면서 현재 레이블일 확률 = 다음 음절 나올 확률,
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





#배치 적용중인 로그라이크리후드

def _log_likelihood(params, *args):
	"""
	Calculate likelihood and gradient
	"""
	global is_batch
	global SUB_ITERATION_NUM
	global train_data
	training_data, feature_set, training_feature_data, empirical_counts, label_dic, squared_sigma, crf = args
	expected_counts = np.zeros(len(feature_set))
	total_logZ = 0


	if SUB_ITERATION_NUM == 0 and is_batch:
		global feature_data
		data, is_end = crf.CRF_bat.return_corpus()
		if is_end:
			crf.CRF_bat.set_file_curser_front()
			crf.feature_set.scan(data,batch=True)
		train_data = None
		training_feature_data = crf._get_training_feature_data(data)
		train_data = training_feature_data
	elif is_batch:
		training_feature_data = train_data

	i = 0
	import time
	for	X_features in training_feature_data:
		#X_features = 한문장
		potential_table = _generate_potential_table(params, len(label_dic), feature_set,
													X_features, inference=False)
	
		alpha, beta, Z, scaling_dic = _forward_backward(len(label_dic), len(X_features), potential_table)
		
		#Z =(제일 마지막 X일때 모든 레이블 확률의 합)
		#scaling_coef..= 오버플로우발생했을때 값들
		#맨 마지막 행 그리고 오버플로우가 뭔가 의미가..
	
		total_logZ += log(Z) + \
					  sum(log(scaling_coefficient) for _, scaling_coefficient in scaling_dic.items())

		#t는 몇번째 음절인지.
		for t in range(len(X_features)):
			#0번째 음절의 확률 테이블 (y,y)크기에 prev_y,y = 확률 값

			potential = potential_table[t]
			for (prev_y, y), feature_ids in X_features[t]:
				# Adds p(prev_y, y | X, t)
				# print (prev_y)
				# print (y)
				if prev_y == -1:
					#
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
						#이전 음절이면서 레이블 나올 확률 * prev_y,y가 나올 모든 확률 *현재
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

	

	sub_iteration_str = '	'
	if SUB_ITERATION_NUM >= 0:
		sub_iteration_str = '(' + '{0:02d}'.format(SUB_ITERATION_NUM) + ')'
	
	#if print('  ', '{0:03d}'.format(ITERATION_NUM), sub_iteration_str, ':', likelihood * -1)
	if is_batch:
		print_str = "번째 배치"
	else:
		print_str = "번째 iteration"
	print('\n({0:03d})'.format(ITERATION_NUM+1),'번째 %s' %(print_str),sub_iteration_str,'번째 sub iteration', ':', likelihood * -1)

	
	result = 0
	for i in range(len(gradients)):
		result += gradients[i]
	
	print( '    gradients:', result/len(gradients))
		
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
	CRF_bat = None
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
	
	
	def _get_training_feature_data(self,data=None):
		if data == None:
			data = self.training_data
		return [[self.feature_set.get_feature_list(X, t) for t in range(len(X))]
				for X, _ in data]
	

	def _estimate_parameters(self,max_iter=None):
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
		global is_batch

		training_feature_data = None
		
		if max_iter == None:max_iter = 5

		if is_batch:
			self.training_data = None
		else:
			print('* Squared sigma:', self.squared_sigma)
			print('* Start L-BGFS')
			print('   ========================')
			print('   iter(sit): likelihood')
			print('   ------------------------')
			training_feature_data = self._get_training_feature_data()

		"""
		print('* Squared sigma:', self.squared_sigma)
		print('* Start L-BGFS')
		print('   ========================')
		print('   iter(sit): likelihood')
		print('   ------------------------')	
		"""

		iteration_start = time.time()
		self.params, log_likelihood, information = \
				fmin_l_bfgs_b(func=_log_likelihood, fprime=_gradient,
							  x0=self.params,
								args=(self.training_data, self.feature_set, training_feature_data,
									self.feature_set.get_empirical_counts(),
									self.label_dic, self.squared_sigma,self),
								maxiter=max_iter,
								callback=_callback)


		
		"""
		print('   ========================')
		print('   (iter: iteration, sit: sub iteration)')
		print('* Training has been finished with %d iterations' % information['nit'])
		print("iteration ended time =",time.time() - iteration_start)
		"""
		
		#if information['warnflag'] != 0:
			#print('\n* Warning (code: %d)' % information['warnflag'])
			#if 'task' in information.keys():
				#print('* Reason: %s' % (information['task']))
		#print('* Likelihood: %s' % str(log_likelihood))

		
	#without batch
	def train(self, corpus_filename, model_filename,batch=None,epoch=None):
		"""
		Estimates parameters using conjugate gradient methods.(L-BFGS-B used)
		"""
		
		start_time = time.time()
		print('[%s] Start training' % datetime.datetime.now())
		if batch == None:
			
			# Read the training corpus
			print("* Reading training data ...")
			self.training_data = self._read_corpus(corpus_filename)
			print('* Read training data complete')
			# Generate feature set from the corpus
			self.feature_set = FeatureSet()
			self.feature_set.scan(self.training_data)
			self.label_dic, self.label_array = self.feature_set.get_labels()
			self.num_labels = len(self.label_array)
			
			print("* Number of labels: %d" % (self.num_labels-1))
			print("* Number of features: %d" % len(self.feature_set))

			# Estimates parameters to maximize log-likelihood of the corpus.
			self.params = np.zeros(len(self.feature_set))
			self._estimate_parameters(max_iter=epoch)
			self.save_model(model_filename)

		else:
			self.train_batch(corpus_filename,model_filename,batch=batch,epoch=epoch)
		
		elapsed_time = time.time() - start_time
		print('* 총 소요 시간 Elapsed time: %f' % elapsed_time)
		print('* [%s] Training done' % datetime.datetime.now())
	
	def train_batch(self, corpus_filename,model_filename,batch=None,epoch=None):
		global is_batch
		is_batch = True
		i = 0
		if epoch == None:
			epoch = 2
		batch = int(batch)
		epoch = int(epoch)
		self.CRF_bat = CRF_batch.CRFBatch(corpus_filename,batch)
		self.feature_set = FeatureSet()
		print("* Reading training data for make whole feature...")
		self.training_data = self._read_corpus(corpus_filename)
		print('* Read training data complete')
		self.feature_set.scan(self.training_data)

		self.label_dic, self.label_array = self.feature_set.get_labels()
		self.num_labels = len(self.label_array)
		print("* Number of labels: %d" % (self.num_labels-1))
		print("* Number of features: %d" % len(self.feature_set))
		self.params = np.zeros(len(self.feature_set))
		self._estimate_parameters(max_iter=epoch * batch)
		self.save_model(model_filename)




	#가다듬기
	#CRF.inference_sentense("문장입니다.",model_filename,False)
	def inference_sentense(self,model):
		self.load(model)
		if self.params is None:
			raise BaseException("You should load a model first!")
		start_time = time.time()
		emjeol_list = list()
		sentense = input("input sentense:")
		emjeol_list = syllable_tokenize(sentense,"korean") 
		Y_list = list()
		for X in emjeol_list:
			Yprime = self.inference(X)
			for i in range(len(Yprime)):
				Y_list.append((X[i],Yprime[i]))
		return Y_list


	def inference_batch(self, test_corpus_filename,model,batch=None):
		batch = int(batch)
		emjeol_file,file_len = utils.make_emjeol_file(test_corpus_filename)
		with open((model+'emjeol').split('.')[0]+'.result','w') as f:
			pass

		with open(emjeol_file,'r') as f:
			for i in range(batch):
				YY_list = list()
				#배치사이즈마다 결과 출력 및 메모리초기화(YY_list=list())
				X = list()
				for count in range(0,int(file_len/iteration)):
					line = f.readline()

					while(line):
						if line != "\n":
							X.append(line.rstrip('\n'))
						else:
							#맨처음에 개행문자가 오는 경우 방지
							if len(X) != 0:
								Yprime = self.inference(X)
								for j in range(len(Yprime)):
									YY_list.append(X[j] + '\t' + Yprime[j])
								YY_list.append('\n')
								X = list()

						line = f.readline()
				file_name = utils.write_inference_result(YY_list ,model+'emjeol',iteration)
			
			print("pred file:",file_name)



	def inference_file(self, test_corpus_filename,model,batch=None):
		self.load(model)
		if self.params is None:
			raise BaseException("You should load a model first!")
		start_time = time.time()
		emjeol_list = list()
		#Y_list = list()
		YY_list = list()
		
		if batch == None:	
			emjeol_list = utils.return_emjeol_list_from_file(test_corpus_filename)
		else:
			batch = int(batch)
			CRF_bat = CRF_batch.CRFBatch(test_corpus_filename,batch) 
			emjeol_file,file_len = utils.make_emjeol_file(test_corpus_filename)
			
		if batch == None:
			for i in range(len(emjeol_list)):
				for X in emjeol_list[i]:
					Yprime = self.inference(X)
					for j in range(len(Yprime)):
						#is_first = 0
						#if j == 0:
							#is_first = 1
						#Y_list.append(str(is_first) + '\t' + X[j] + '\t' +Yprime[j])
						YY_list.append(X[j] + '\t' + Yprime[j])
			utils.write_inference_result(YY_list ,model+'emjeol')

		else:
			#리스트로 가지고 있지 않고 하나하나출력하는 방법
			self.inference_batch(test_corpus_filename,model,batch=batch )
			
		#마킹기반 어절 + 예측한 형태소
		#word_Y = utils.return_converted_word_from_emjeol(Y_list)
		#model파일이름.result에 저장
		#utils.write_inference_result(word_Y,model)




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
		fea_dic = self.feature_set.serialize_feature_dic()
		model = {"feature_dic": fea_dic,
				 "num_features": self.feature_set.num_features,
				 "labels": self.feature_set.label_array,
				 "params": list(self.params)}
		f = open(model_filename, 'w')
		json.dump(model, f, ensure_ascii=False, indent=2, separators=(',', ':'))
		f.close()	
		import os
		print('* Trained CRF Model has been saved at "%s/%s"' % (os.getcwd(), model_filename))
		

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


	def load(self, model_filename):
		try:
			f = open(model_filename,encoding='utf-8')
			model = json.load(f)
			f.close()
		except Exception as e:
			f = open(model_filename,encoding="cp949")
			model = json.load(f)
			f.close()

		self.feature_set = FeatureSet()
		self.feature_set.load(model['feature_dic'], model['num_features'], model['labels'])
		self.label_dic, self.label_array = self.feature_set.get_labels()
		self.num_labels = len(self.label_array)
		self.params = np.asarray(model['params'])
		print('CRF model loaded')

	

"""
백업
	def inference_file(self, test_corpus_filename,model):
		self.load(model)
		if self.params is None:
			raise BaseException("You should load a model first!")
		start_time = time.time()
		emjeol_list = list()
		emjeol_list = utils.return_emjeol_list_from_file(test_corpus_filename)
		#마킹 + 음절+ 예측한 형태소
		Y_list = list()
		YY_list = list()
		for i in range(len(emjeol_list)):
			for X in emjeol_list[i]:
				Yprime = self.inference(X)
				for j in range(len(Yprime)):
					is_first = 0
					if j == 0:
						is_first = 1
					Y_list.append(str(is_first) + '\t' + X[j] + '\t' +Yprime[j])
					YY_list.append(X[j] + '\t' + Yprime[j])
		#마킹기반 어절 + 예측한 형태소
		#word_Y = utils.return_converted_word_from_emjeol(Y_list)
		#model파일이름.result에 저장
		#utils.write_inference_result(word_Y,model)
		utils.write_inference_result(YY_list ,model+'emjeol')
"""



if __name__ == '__main__':
	crf = LinearChainCRF()
	model = "delete.model"
	model2 = "delete2.model"
	test_corpus_filename = "1000.dat"

	import os
	path = os.path.join(os.path.abspath(os.path.dirname(__file__)),test_corpus_filename)
	#crf.train(path,model2,epoch=2)
	crf.train(path, model, batch=2,epoch=2)
