# -*- coding: utf-8 -*-

import make_eumjeol_corpus as make_eumjeol
from nltk.tokenize import word_tokenize
from crf_make_eumjeol import start



class kr_tokenizer():

	'''
	목표
	raw data를
	나는	나/NP+는/JX
	감기에	감기/NNG+에/JKS
	걸렸다.	걸리/W+었/EP+다/EF+./SF
	로 변환 (어절 토크나이저 + 형태소 분석기)


	나	나/NP
	는	는/JX
	...
	로 변환 (음절 토크나이저)
	이때 복합 명사같은 경우에 주의하여 구현

	형태소 부분은 NP JX 등 정보 모르니까 일단 CO로 표현하자
		

	
	
	'''
	def __init__(self):
		pass

	def test_code(self):
		print('just_print',self.return_emjeol_from_raw("이름이 박찬양인 사람"))
		print('suc',self.return_emjeol_from_word("이름이")[0] == "이")
		print('fail',self.return_word_tok_from_raw("이름이 박찬양인 사람")[0] != "이름이")

	def return_word_tok_from_raw(self,raw_data = ""):
		return word_tokenize(raw_data,'korean')

	def make_emjeol_n_morph_from_word_file(self,filename):
		print('file:',start(filename))

	def return_emjeol(self,raw_data):
		return [emjeol for emjeol in raw_data if emjeol != ' ']


		

def test(prediction_filename,anwser_filename):
	with open(anwser_filename,'r') as f:
		anwser_list = f.readlines()
		re_anwser = list() 
		for line in anwser_list:
			if line != '\n':
				re_anwser.append(line)
	
	with open(prediction_filename,'r') as f2:
		pred_list = f2.readlines()
		re_pred_list = list()
		for line in pred_list:
			if line != '\n':
				re_pred_list.append(line)
	from nltk.metrics import accuracy
	print('result:',accuracy(re_anwser,re_pred_list))



if __name__ == "__main__":
	tok = kr_tokenizer()
	tok.test_code()
	import sys
	sys.exit()
	filename =""

	
	string = "저는 박찬양입니다"
	emjeol_list = tok.return_emjeol_from_raw(string)
#	test(filename)



'''

	#형태소 부분 어떻게 쪼갤지...
	#방법 2 고려
	def return_emjeol_from_word_modify(self,word):

		tmp = word.split('\t')
		word,pos = self.seperate_word_n_pos(tmp[1])
		emjeol_list = list()

		ori_word = tmp[0]
		ori_idx = 0

		
		i = 0
		while(i < len(word)):
			#음절 쪼개기
			for j in range(len(word[i])):
				if len(ori_word) < ori_idx:
					break

				if len(ori_word) < ori_idx+1:
					print('*',word[i][j],'을 아래걸로바꿈')
					emjeol_list.pop()
					result = ori_word[i-1] + '\tCO'
					print("result=",result)
					input()
				elif word[i][j] == ori_word[ori_idx]:
					result = word[i][j] + '\t' + pos[i]

				else:
					result = ori_word[ori_idx] + '\tCO'
					print('#',end='')
					print("result=",result)
					input()
					emjeol_list.append(result+'\n')
					ori_idx+=1
					i+=1
					break
				ori_idx+=1
				#print('result=',result)
				emjeol_list.append(result+'\n')
			i+=1
		return emjeol_list





	def seperate_word_n_pos(self,pos):
		tmp = pos.split('+')
		pos_list = list()
		word_list = list()
		for i in range(len(tmp)):
			word_list.append(tmp[i].split('/')[0])	
			pos_list.append(tmp[i].split('/')[1])

		return word_list,pos_list


	'''

