# -*- coding: utf-8 -*-

import make_eumjeol_corpus as make_eumjeol
from nltk.tokenize import word_tokenize




class kr_tokenizer():

	'''
	raw data를
	다음과 같은 어절 및 형태소로 분리한 파일로 생성
	나는	나/NP+는/JX
	감기에	감기/NNG+에/JKS
	걸렸다.	걸리/W+었/EP+다/EF+./SF
	형태소 부분은 NP JX 등 정보 모르니까 일단 CO로 표현하자
	'''
	i = 0


	def return_word_tok_from_raw(self,raw_data = ""):
		word_tok = word_tokenize(raw_data,'korean')
		result_word = list()
		for word in word_tok:
			pos = self.return_pos_from_word(word)
			result_word.append(word+'\t'+pos)

		return result_word
	
	#형태소 분석기 필요
	def return_pos_from_word(self,word_tok):
		morpheme = word_tok + '/CO-'+str(self.i)
		self.i =self.i + 1
		
		return morpheme

	#사람에게
	def return_emjeol_from_raw(self,raw_data):
		word_tok = return_word_tok_from_raw(self,raw_data)
		result_emjeol_list = list()
		for word in word_tok:
			emjeol_list = return_emjeol_from_word(word)
			result_emjeol_list.append(emjeol_list)
		
		return result_emjeol_list

	def return_emjeol_from_word(self,word):

		tmp = word.split('\t')
		if(len(tmp)==1):
			return ""
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
		
	
def test(filename):
	
	data = "안녕하세요 박찬양입니다."  
	tok = kr_tokenizer()
	data = tok.return_word_tok_from_raw(data)
	for i in data:
		data = tok.return_emjeol_from_word(i)
		for j in data:
			print(j)
	

if __name__ == "__main__":
	tok = kr_tokenizer()
	filename =""
	test(filename)

