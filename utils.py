# -*- coding: utf-8 -*-

from nltk import korChar
from nltk.tokenize import word_tokenize,syllable_tokenize
import re

#추론 결과파일 이름 중복되지 않게
# filename0.result
def return_no_duplicated_filename(filename):
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

#CRF_lib.py로
def return_emjeol_list_from_file(filename):
	content = return_file_content(filename)
	word = return_word(content)
	emjeol_list = return_emjeol(word)
	return emjeol_list
		
def make_emjeol_file(sentense_filename):
	f_length = 0
	file_name = sentense_filename.split('.')[0]+'.gld'
	with open(sentense_filename,'r',encoding='cp949') as fr:
		with open(file_name,'w') as fw:
			line = fr.readline()
			result = list()
			word_list = list()
			while(line):
				word_list = word_tokenize(line,'korean')
				for word in word_list:
					emjeol_list = syllable_tokenize(word,'korean')
					for emjeol in emjeol_list:
						fw.write(emjeol+'\n')
						f_length+=1
				fw.write('\n')
				f_length+=1
				line = fr.readline()
	return file_name, f_length 		
	


def return_file_content(filename):
	try:
		with open(filename,'r',encoding='cp949') as f:
			return f.readlines()
	except:
		with open(filename,'r') as f:
			return f.readlines()

def return_word(content):
	word_list = list()
	for line in content:
		word_list.append(word_tokenize(line,'korean'))

	return word_list


def return_emjeol(word_list):
	emjeol_list = list()
	word_sentense_unit_list = list()
	word_sentense = ""
	for word in word_list:
		word_sentense =""
		for i in word:
			word_sentense += i
		emjeol_list.append(syllable_tokenize(word_sentense,'korean'))
	return emjeol_list



def return_converted_word_from_emjeol(Y):
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


# CRF_lib로 빼자
def write_inference_result(Y_list,filename,iteration = None):
	output_file = filename.split('.')[0]+'.result'

	if iteration == None:
		with open(output_file,'w') as f:
			for line in Y_list:	
				if line != '\n':
					f.write(line+'\n')
				else:
					f.write('\n')

		print('result prediction file:',output_file)
	else:
		with open(output_file,'a') as f:
			for line in Y_list:
				if line != '\n':
					f.write(line+'\n')
				else:
					f.write('\n')


		return output_file				
	



def test(prediction_filename,anwser_filename):

	with open(anwser_filename,'r') as f:
		anwser_list = f.readlines()
		re_anwser = list() 
		for line in anwser_list:

			if line != '\n' and len(line.split('\t')) > 1:
				re_anwser.append(line)

	with open(prediction_filename,'r') as f2:
		pred_list = f2.readlines()
		re_pred_list = list()
		for line in pred_list:
			if line != '\n' and len(line.split('\t')) > 1:
				re_pred_list.append(line)
	from nltk.metrics import accuracy

	for i in range(len(re_pred_list)):
		if re_pred_list[i] != re_anwser[i]:
			print("P:",re_pred_list[i]+"A:",re_anwser[i])

	print('result:',accuracy(re_anwser,re_pred_list))



#CRF lib로
def is_meta_syllable(value):
	try:
		if len(value) == 0 or value == '' or value == ' ':
			return '휅'
		if korChar.num_syllable(value):
			return '1'
		if korChar.eng_syllable(value):
			return 'A'
		if korChar.hanja_syllable(value):
			return '家'
		return value
	except Exception as e:
		return '휅'


def return_rowNcol(element):
	return re.findall(r'-?\d+',element)


# 음절	형태소 형식의 파일에서
# 음절부분만 가져와 문장으로 만듦
def emjeol_to_sentense(filename):
	with open(filename,'r') as f:
		data =f.readlines()
		sentense_list = list()
		sentense = ""
		for line in data:

			splited_line = line.split('\t')
			x = splited_line[0]
			if len(splited_line) == 0 or len(splited_line) == 1:
				sentense_list.append(sentense)
				sentense = ""
			else:
				sentense += x
		sentense_list.append(sentense)

	with open(filename.split('.')[0]+"_sentense.dat",'w') as f:
		for i in sentense_list:
			f.write(i+'\n')



def write_anyway(thing):
	"""
	training_feature_data
	"""

	'''
	모든 X에 대한.
	즉[[(prev_y,y),id)] in X] in whole_data
	'''
	f = open('test.txt','w')

	for i in thing:
		'''
		[(prev_y,y),id)] - X 단위.
		X는 한 문장의 모든 음절의 리스트
		X
		['양'], ['반'], ['네'], ['들'], ['앞'], ['에'], ['서'],
		['그'], ['네'], ['들'], ['조'], ['롱']....
		'''
		for j in i:
			"""
			(prev_y,y),id
			"""
			for k,n in j:
				str_tmp = "("
				for m in list(k):
					str_tmp += str(m) +','
				str_tmp = str_tmp.rstrip(',')+(')')
				print(str_tmp.rstrip(',')+')')
				f.write(str_tmp + ':' + str(n)+', ')

			
			f.write('\n')




if  __name__ == "__main__":
	file_name = "test.gld"

	data = "./no_batch_model0.result"
	data2 = "./batch_model0.result"
	test(data,data2)
	#emjeol_to_sentense(file_name)



