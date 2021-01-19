#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import Counter
import sys
import numpy as np
import re
import utils
STARTING_LABEL = '*'		# Label of t=-1
STARTING_LABEL_INDEX = 0

#템플릿..이건 어카지
def feature_setting(_, X, t):
	"""
	Returns a list of feature strings.
	(Default feature function)
	:param X: An observation vector
	:param t: time
	:return: A list of feature strings
	"""
	length = len(X)

	import os
	path = os.path.join(os.path.abspath(os.path.dirname(__file__)),'template')
	f = open(path,'r',-1,'utf-8')
	f.readline()

	line = f.readlines()
	features = list()
	feature = ""
	a = ""
	for i in range(len(line)):
		'한줄씩 템플릿에서 불러와서 feature 생성'
		tmp_line = line[i]
		if len(tmp_line) == 1:
			continue
		if tmp_line.find(':') == -1:
			continue
		key = tmp_line.split(':')[0]
		element_arr = tmp_line.split(':')[1].split('/')

		feature = tmp_line.rstrip('\n') + '='
		value = ""
		for j in range(len(element_arr)):
			
			element = element_arr[j].rstrip('\n')
			row, col = utils.return_rowNcol(element)
			row = int(row)
			col = int(col)
			if row > length-t-1 and row >= 0:
				break
			elif row + t < 0 and row < 0:
				break
			
			value = X[t+int(row)][int(col)]
			if value != '\n':
				value = utils.is_meta_syllable(value)	

			feature += value + '/'
		if len(value) != 0:

			features.append(feature.rstrip('/'))
	f.close()
	return features


	
class FeatureSet():

	count_x = 0
	feature_dic = dict()
	observation_set = set()
	empirical_counts = Counter()
	num_features = 0

	label_dic = {STARTING_LABEL: STARTING_LABEL_INDEX}
	label_array = [STARTING_LABEL]
	#feature_func = default_feature_func
	feature_func = feature_setting
	
	def _init(self):
		feature_dic = dict()
		bservation_set = set()
		empirical_counts = Counter()
		num_features = 0

		label_dic = {STARTING_LABEL: STARTING_LABEL_INDEX}
		label_array = [STARTING_LABEL]
		#feature_func = default_feature_func
		feature_func = feature_setting



	def __init__(self, feature_func=None):
		# Sets a custom feature function.
		if feature_func is not None:
			self.feature_func = feature_func


	def empirical_init(self):
		emp_length = len(self.empirical_counts)
		for i in range(emp_length):
			self.empirical_counts[i] = 0
	

	def	empirical_recount(self, prev_y, y, X, t):
		for feature_string in self.feature_func(X, t):
			key = feature_string[0]
			if key != 'U':
				feature_id = self.feature_dic[feature_string][(prev_y,y)]
				self.empirical_counts[feature_id] += 1
			else:
				feature_id = self.feature_dic[feature_string][(-1,y)]
				self.empirical_counts[feature_id] += 1

	def scan(self, data,batch=False):
		"""
		Constructs a feature set, a label set,
			and a counter of empirical counts of each feature from the input data.
		:param data: A list of (X, Y) pairs. (X: observation vector , Y: label vector)
		"""
		# Constructs a feature set, and counts empirical counts.]
		idx = 0
		if batch:self.empirical_init()
		for X, Y in data:
			prev_y = STARTING_LABEL_INDEX
			for t in range(len(X)):
				# Gets a label id
				try:
					y = self.label_dic[Y[t]]
				except KeyError:
					y = len(self.label_dic)
					self.label_dic[Y[t]] = y
					self.label_array.append(Y[t])
				# Adds features
				if batch:self.empirical_recount(prev_y,y,X,t)
				else:self._add(prev_y, y, X, t)
				prev_y = y



	def load(self, feature_dic, num_features, label_array):
		self.num_features = num_features
		self.label_array = label_array
		self.label_dic = {label: i for label, i in enumerate(label_array)}
		self.feature_dic = self.deserialize_feature_dic(feature_dic)

	def __len__(self):
		return self.num_features
	
	def adding_features_into_dict(self,feature_string,prev_y,y):
		feature_id = self.num_features
		self.feature_dic[feature_string][(prev_y, y)] = feature_id
		#if CRF_bat is not None:
			#CRF_bat.feature_io.write_feature_into_file(feature_string,prev_y,y,feature_id)
		self.empirical_counts[feature_id] += 1
		self.num_features += 1
	
		
	

	#code refactoring
	def _add(self, prev_y, y, X, t,CRF_bat=None):
		"""
		Generates features, constructs feature_dic.
		:param prev_y: previous label
		:param y: present label
		:param X: observation vector
		:param t: time
		"""

		for feature_string in self.feature_func(X, t):
			#print("피쳐 스트링=",feature_string)
			#현재 단어가 피쳐 딕셔너리 키에 있다
			key = feature_string[0]

			if feature_string in self.feature_dic.keys():
				if key != 'U':
					#현재 단어의 prev y 랑 y가 이미 딕셔너리 피쳐에 있다
					if (prev_y, y) in self.feature_dic[feature_string].keys():
						self.empirical_counts[self.feature_dic[feature_string][(prev_y, y)]] += 1
					else:
						#없으면 prev y랑 y 피쳘 딕셔너리에 추가
						self.adding_features_into_dict(feature_string,prev_y,y)

				#prev y랑 y 가 -1,y 가여도 피쳐 딕셔너리에 이미 있으면 임페리컬 카운트 증가
				else:
					if (-1, y) in self.feature_dic[feature_string].keys():
						self.empirical_counts[self.feature_dic[feature_string][(-1, y)]] += 1
					else:
						self.adding_features_into_dict(feature_string,-1,y)
			else:
				# 현재 피쳐 스트링이 피쳐 딕셔너리에 없다 (처음 나왔다)
				self.feature_dic[feature_string] = dict()
				#prev y , y추가
				if key != 'U':
					self.adding_features_into_dict(feature_string,prev_y,y)
				else:
					self.adding_features_into_dict(feature_string,-1,y)
	

							

	def get_feature_vector(self, prev_y, y, X, t):
		"""
		Returns a list of feature ids of given observation and transition.
		:param prev_y: previous label
		:param y: present label
		:param X: observation vector
		:param t: time
		:return: A list of feature ids
		"""
		feature_ids = list()
		for feature_string in self.feature_func(X, t):
			try:
				feature_ids.append(self.feature_dic[feature_string][(prev_y, y)])
			except KeyError:
				pass
		return feature_ids

	def get_labels(self):
		"""
		Returns a label dictionary and array.
		"""
		return self.label_dic, self.label_array

	def calc_inner_products(self, params, X, t):
		"""
		Calculates inner products of the given parameters and feature vectors of the given observations at time t.
		:param params: parameter vector
		:param X: observation vector
		:param t: time
		:return:
		"""
		inner_products = Counter()
		for feature_string in self.feature_func(X, t):
			#각 어절
			try:
				# 각 어절의 prev y ,y
				# 이전 피쳐가 처음인 단어인데 그 다음 피쳐가 -1 , y?
				for (prev_y, y), feature_id in self.feature_dic[feature_string].items():
					inner_products[(prev_y, y)] += params[feature_id]
			except KeyError:
				pass
		return [((prev_y, y), score) for (prev_y, y), score in inner_products.items()]

	def get_empirical_counts(self):
		empirical_counts = np.ndarray((len(self.empirical_counts),))

		for feature_id, counts in self.empirical_counts.items():
			empirical_counts[feature_id] = counts
		return empirical_counts

	def get_feature_list(self, X, t):
		feature_list_dic = dict()
		#if self.count_x % 500 == 0 and self.count_x != 0:
		#	print(self.count_x,"번째")
		#self.count_x += 1

		for feature_string in self.feature_func(X, t):
			for (prev_y, y), feature_id in self.feature_dic[feature_string].items():
				if (prev_y, y) in feature_list_dic.keys():
					feature_list_dic[(prev_y, y)].add(feature_id)
				else:
					feature_list_dic[(prev_y, y)] = {feature_id}
		return [((prev_y, y), feature_ids) for (prev_y, y), feature_ids in feature_list_dic.items()]

	def serialize_feature_dic(self):
		serialized = dict()
		for feature_string in self.feature_dic.keys():
			serialized[feature_string] = dict()
			for (prev_y, y), feature_id in self.feature_dic[feature_string].items():
				serialized[feature_string]['%d_%d' % (prev_y, y)] = feature_id
		return serialized

	def deserialize_feature_dic(self, serialized):
		feature_dic = dict()
		for feature_string in serialized.keys():
			feature_dic[feature_string] = dict()
			for transition_string, feature_id in serialized[feature_string].items():
				prev_y, y = transition_string.split('_')
				feature_dic[feature_string][(int(prev_y), int(y))] = feature_id
		return feature_dic


