#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
@Author: Jeong-Won Cha
@Description:
	
	[input]
	어절<tab><tab>형태소 분석
	
	형태의 문서를 입력받아 다음과 같은 형태로 변환한다.

	[output]
	음절<tab>품사


BUGS

'''

import sys
import glob
import re
from io import StringIO
import parse_morph_sejong
import libKoreanString

enc = "utf-8"
mapping_table = {"NNG":"NN", "NNP":"NN", "NNB":"NN", "NP":"NN", 
		"XR":"NN", "NR":"NN", 
		"VV":"VB", "VA":"VB", "VCP":"VB", "VCN":"VB","VX":"VB",
		"MM":"MM", "MAG":"MA", "MAJ":"MA",
		"JKS":"JJ", "JKB":"JJ", "JKC":"JJ", "JKG":"JJ", "JKO":"JJ", "JKV":"JJ", "JX":"JJ", "JC":"JJ", "JKQ":"JJ",
		"EC":"EE", "EF":"EE", "ETN":"EE", "ETM":"EE", "EP":"EE",
		"XPN":"NN", "XSN":"XN", "XSV":"XV", "XSA":"XV",
		"SH":"SH", "SN":"SN", "SL":"SL",
		"SS":"SY", "SO":"SY", "SP":"SY", "SW":"SY", "SE":"SY", "SF":"SY",
		"IC":"IC",
		"NA":"NA"}

eumjeol_dict = dict()
"""
	온VE	온	VB ㄴ EE
"""

"""
세종형태의 형태소 입력을 받아서 

말	말	NNG	
한	하	XSV	ㄴ	EF	
다	다	EF	
.	.	SF	

형태의 파일을 출력한다. 
"""
def step1_make_temp_file(Inf):
	f = open(Inf[0])
	lines = f.readlines()
	f.close()
	
	outputfilename = "_eumjeol_s1.txt"
	output_f = open(outputfilename, "w")

	print("input : " + Inf[0])
	print("output : " + outputfilename)



	for line in lines:

		if line == '\n':
			output_f.write("\n")
			continue

		if line == '\r\n':
			output_f.write('\r\n')
			continue

		result = line.strip().split('\t')
		result_morph = parse_morph_sejong._parse_morph_sejong(result[1])
		#eojeol = str(result[0],"utf-8")
		eojeol = result[0]
		#원본1
		#eojeol = unicode(result[0], enc)
		

		mL = list()
		for m, t in result_morph:
			#원본2
			#m = unicode(m, enc)
			
			s = 0
			for e in range(1, len(m)+1):
				mL.append((m[s:e], t))
				s = e

#			for m, t in mL:
#				output_f.write("%s\t%s\t%s\n" % (eojeol.encode(enc), m.encode(enc), t))
	
		# collect the same word
		s = 0
		i = 0
		eD = dict() # eojeol dict
		for s in range(len(eojeol)) :
			k = str(s) + eojeol[s:s+1]
			eD[k] = list()
			#print s, eojeol[s:s+1], eojeol, mL, i, mL[i-1][0]
			if i < len(mL) and eojeol[s:s+1] == mL[i][0]:
				eD[k].append(i)
				i += 1
				s += 1
			elif i < len(mL)-1 and eojeol[s:s+1] == mL[i+1][0]:
				i += 1
				#eD[k].append(i)
				if len(eojeol)-s <= len(mL)-i: eD[k].append(i)
				else: 
					i -= 1
					eD[k].append(-1)
			elif i < len(mL)-2 and eojeol[s:s+1] == mL[i+2][0]:
				i += 2
				#eD[k].append(i)
				if len(eojeol)-s <= len(mL)-i: eD[k].append(i)
				else: 
					i -= 2
					eD[k].append(-1)
			elif i < len(mL)-3 and eojeol[s:s+1] == mL[i+3][0]:		# 왔다갔다했다 -> 오았다가았다하았다
				i += 3
				#eD[k].append(i)
				if len(eojeol)-s <= len(mL)-i: eD[k].append(i)
				else: 
					i -= 3
					eD[k].append(-1)
			elif eojeol[s:s+1] == mL[i-1][0] and eojeol[s:s+1] != eojeol[s-1:s]:
				i -= 1
				eD[k].append(i)
			elif i > 2 and eojeol[s:s+1] == mL[i-2][0] and eojeol[s:s+1] != eojeol[s-2:s-1]:
				i -= 2
				eD[k].append(i)
			else:
				eD[k].append(-1)
				i += 1
		
		# put something to the blank 
		i = 0
		for s in range(len(eojeol)) :
			k = str(s) + eojeol[s:s+1]
			if eD[k][0] == -1:			# 다른 경우 
				if (s == 0) or (s>0 and eD[str(s-1)+eojeol[s-1:s]][-1] != -1 ):
					#output_f.write("%s\n" % mL[0][0].encode(enc))
					if s ==0 : i = 0
					elif re.findall(u'우', eojeol[s:s+1]) and libKoreanString.splitCJJ(mL[i-1][0])[2] == u'ㅂ':
						i = eD[str(s-1)+eojeol[s-1:s]][-1]
						#output_f.write("%d>>%s\t%s\n" % (i, eojeol[s:s+1].encode(enc), libKoreanString.splitCJJ(mL[i-1][0])[2].encode(enc)))
					else: i = eD[str(s-1)+eojeol[s-1:s]][-1]+1
					eD[k][0] = i
					i += 1
					# 뒤에 연속으로 비어 있으면 하나 더 추가. 이것은 연속일 경우에 2:2인 경우이기 때문임 
					# 예외: 무거워져갔다. -> 무겁어지어가았다.
					if s <= len(eojeol)-2 and libKoreanString.splitCJJ(eojeol[s:s+1])[2] == u'ㄹ' and (re.findall(u'러', eojeol[s+1:s+2]) or re.findall(u'라', eojeol[s+1:s+2])):
						pass
					elif s <= len(eojeol)-2 and libKoreanString.splitCJJ(mL[eD[k][0]][0])[2] == u'ㅂ' and \
							libKoreanString.splitCJJ(eojeol[s+1:s+2])[0] == u'ㅇ' and (libKoreanString.splitCJJ(eojeol[s+1:s+2])[1] == u'ㅝ' or libKoreanString.splitCJJ(eojeol[s+1:s+2])[1] == u'ㅜ'):
						pass
					elif s >0 and libKoreanString.splitCJJ(mL[eD[str(s-1)+eojeol[s-1:s]][0]][0])[2] == u'ㅂ' and \
							libKoreanString.splitCJJ(eojeol[s:s+1])[0] == u'ㅇ' and (libKoreanString.splitCJJ(eojeol[s:s+1])[1] == u'ㅝ' or libKoreanString.splitCJJ(eojeol[s:s+1])[1] == u'ㅜ'):
						pass
					elif s <= len(eojeol)-2 and eD[str(s+1)+eojeol[s+1:s+2]][0] == -1 and len(mL)-i-(len(eojeol)-s) >= 1 :
						eD[k].append(i)
						i += 1
			
					# 복수의 비어 있는 것을 추가하는 부분 
					while (s < len(eojeol)-1 and eD[str(s+1)+eojeol[s+1:s+2]][0] != -1 and  i < eD[str(s+1)+eojeol[s+1:s+2]][0]) \
						or (s == len(eojeol)-1 and i < len(mL)):
						#if s < len(eojeol)-1: output_f.write(">>%s----%d\n" % (eojeol[s+1:s+2].encode(enc), eD[str(s+1)+eojeol[s+1:s+2]][0]))
						eD[k].append(i)
						i += 1

		for s in range(len(eojeol)):
			k = str(s)+eojeol[s:s+1]
			if eD[k][0] != -1:
				output_f.write("%d\t" % (1 if s == 0 else 0))
				output_f.write("%s\t" % k[len(str(s)):])
				for i in eD[k]:
					output_f.write("%s\t%s\t" % (mL[i][0], mL[i][1]))
				output_f.write("\n")
			else:
				output_f.write("%s\t%s\t%s\n" % (k, "--" , "--"))
			
	output_f.close()

	return outputfilename

""" 
temp 파일을 읽어서 다음과 같은 최종본과 사전을 생성한다.

말	말	NN	
한	하	XE	
다	다	EE	
.	.	SY	

한XE	하 XS	ㄴ	EE
"""
import struct


def step2_make_eumjeol_file(tF):
	global eumjeol_dict
	f = open(tF)
	lines = f.readlines()
	f.close()
	outputfilename = "_eumjeol.gld"
	output_f = open(outputfilename, "w")

	print("input : " + tF)
	print("output : " + outputfilename)

	line_num = 0
	for line in lines:
		if line[0] == '\n':
			output_f.write("\n")
			line_num = 0
			continue


		result = line.strip().split('\t')
		eumjeolL = list()
		# mapping: 세종 태그셋을 단축셋으로 매핑한다.

		if len(result) <= 4:
			output_f.write ("%s\t%s\n" % (result[1], mapping_table[result[3]]))
		else:
			if result[0] == '1' and (mapping_table[result[3]] == 'NN' or mapping_table[result[3]] == 'MA'):
				output_f.write ("%s\t%s\n" % (result[1], mapping_table[result[3]]))
			else:
				output_f.write ("%s\t%s\n" % (result[1], 'CO'))
						


	
		#eumjeolL.append(umT)
		line_num += 1
		if len(result) <= 4: continue
		for i in range(2, len(result)):
			if i%2 == 1: eumjeolL.append(mapping_table[result[i]])
			else: eumjeolL.append(result[i])
		if not result[i] in eumjeol_dict : eumjeol_dict[result[1]] = set()
		else:
			v = "-".join(eumjeolL)
			eumjeol_dict[result[1]].add(v)
	output_f.close()
	return outputfilename


def start(filename):

	inputfilenames = glob.glob(filename)
	#inputfilenames = glob.glob("tagged/seJongGold2.txt")
	inputfilename = inputfilenames

	for inputfilename in inputfilenames:
		print(inputfilename)
		tempF = step1_make_temp_file(inputfilenames)
		output_e = step2_make_eumjeol_file(tempF)


	
	outputfilename = inputfilename[:inputfilename.rfind('.')] + "_eumjeol.dict"
	outputfilename = "eumjeol"+outputfilename[inputfilename.find('/'):]
	output_f = open(outputfilename, "w")

	for k, v in eumjeol_dict.items():
		if len(v) <= 1: continue
		output_f.write("%s\t\t" % k)
		for vS in v:
			output_f.write("%s\t" % vS)
		output_f.write("\n")
	output_f.close()
	return output_e
	


if __name__=="__main__":

	inputfilenames = glob.glob("mini_Sejong.txt")
	#inputfilenames = glob.glob("tagged/seJongGold2.txt")
	inputfilename = inputfilenames

	for inputfilename in inputfilenames:
		print(inputfilename)
		tempF = step1_make_temp_file(inputfilenames)
		step2_make_eumjeol_file(tempF)

	
	outputfilename = inputfilename[:inputfilename.rfind('.')] + "_eumjeol.dict"
	outputfilename = "eumjeol"+outputfilename[inputfilename.find('/'):]
	output_f = open(outputfilename, "w")

	for k, v in eumjeol_dict.items():
		if len(v) <= 1: continue
		output_f.write("%s\t\t" % k)
		for vS in v:
			output_f.write("%s\t" % vS)
		output_f.write("\n")
	output_f.close()
