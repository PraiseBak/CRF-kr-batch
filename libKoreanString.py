#python-library-file
# -*- coding: utf-8 -*-
###########################################################################
## @file	libKoreanString.py
## @brief	한국어 유틸리티
## 
## 한국어 처리에 필요한 함수 모음
###########################################################################

__all__ = [ "setEncoding", 
	"isHangulChr", 
	"splitCJJ", "joinCJJ",  
	"cmpHangul", 
	"isHangulSyllable", "isHanjaSyllable", "isNumberSyllable", 
	"isAlphabetChr", "isSymbolChr", 
	"isAlphabetConnectionChr", "isNumberConnectionChr"
]

import unicodedata

global _default_encoding
_default_encoding = "utf-8"

CHOSEONG_IDX_CODEMAP = [1, 2, 0, 3, 0, 0, 4, 5, 6, 0, 0, 0, 0, 0, 0, 0, 7, 8, 9, 0, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
JONGSEONG_IDX_CODEMAP= [1, 2, 3, 4, 5, 6, 7, 0, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 0, 18, 19, 20, 21, 22, 0, 23, 24, 25, 26, 27]
getCJamoIdxChoseong  = lambda x: ((x > min(CHOSEONG_IDX_CODEMAP) and x <= max(CHOSEONG_IDX_CODEMAP)) and CHOSEONG_IDX_CODEMAP.index(x)) or 0
getCJamoIdxJongseong = lambda x: ((x > min(JONGSEONG_IDX_CODEMAP) and x <= max(JONGSEONG_IDX_CODEMAP)) and JONGSEONG_IDX_CODEMAP.index(x)) or 0
isCJamoChoseong  = lambda x: (x >= 0x3131 and x <= 0x3130+len(CHOSEONG_IDX_CODEMAP)) and bool(CHOSEONG_IDX_CODEMAP[x-0x3131]) or bool(0)
isCJamoJungseong = lambda x: (x >= 0x314f and x <= 0x3163)
isCJamoJongseong = lambda x: (x >= 0x3131 and x <= 0x3130+len(JONGSEONG_IDX_CODEMAP)) and bool(JONGSEONG_IDX_CODEMAP[x-0x3131]) or bool(0)

###
# @brief	라이브러리용 엔코딩 설정 함수
# 기본 엔코딩 정보를 설정한다
# 
# @param[in]		encoding	문자열 엔코딩 정보
#
# @return	현재 설정된 기본 엔코딩 정보
def setEncoding(encoding = None):
	""" 라이브러리용 엔코딩 설정 함수
	
	기본 엔코딩 정보를 설정한다
	
	인자값 목록 (모든 변수가 반드시 필요):
	
	encoding : 문자열 엔코딩 정보
	
	결과값 : 현재 설정된 기본 엔코딩 정보
	
	"""
	global _default_encoding
	try:
		str("dummy", encoding)
	except:
		return _default_encoding
	
	_default_encoding = encoding or _default_encoding
	return _default_encoding

###
# @brief	한글 문자 판별 함수
# 입력한 문자가 한글 문자인지 판별한다.
# 
# @param[in]		character	문자
# @param[in]		encoding	문자의 엔코딩 정보
#
# @return	한글 문자이면 True, 그렇지 않으면 False
###
def isHangulChr(character, encoding = None):
	""" 한글 문자 판별 함수
	
	입력한 문자가 한글 문자인지 판별한다.
	
	인자값 목록 (모든 변수가 반드시 필요):
	
	character : 문자
	encoding : 문자의 엔코딩 정보
	
	결과값 : 한글 문자이면 True, 그렇지 않으면 False
	
	"""
	global _default_encoding
	encoding = encoding or _default_encoding
	
	if type(character) == str:
		character = character
	elif type(character) != str:
		raise TypeError("parameter type is string or unicode")
	
	ch = ord(character)
	
	return (	( ch >= 0xac00 and ch <= 0xd7af)	or	# Hangul Syllables \\
				( ch >= 0x1100 and ch <= 0x11ff)	or	# Hangul Jamo \\
				( ch >= 0x3130 and ch <= 0x318f)	or	# Hangul Compatibility Jamo \\
				( ch >= 0xffa1 and ch <= 0xffdc)	)	# Hangul Halfwidth

###
# @brief	초/중/종성 분할 함수
# 입력한 문자를 초,중,종성으로 분할해준다.
# 만약, 한글 문자가 아닐 경우, 이 문자를 초성에 결과를 집어넣어 결과를 반환한다.
# 주 ) 아직까지 Hangul Jamo/옛한글 에 대한 처리는 고려하지 않았음
# 
# @param[in]		character	문자
# @param[in]		encoding	문자의 엔코딩 정보
#
# @return	초,중,종성으로 분할된 결과를 list로 반환
###
def splitCJJ(character, encoding = None):
	""" 초/중/종성 분할 함수
	
	입력한 문자를 초,중,종성으로 분할해준다.
	만약, 한글 문자가 아닐 경우, 이 문자를 초성에 결과를 집어넣어 결과를 반환한다.
	주 ) 아직까지 Hangul Jamo/옛한글 에 대한 처리는 고려하지 않았음
	
	인자값 목록 (모든 변수가 반드시 필요):
	
	character : 문자
	encoding : 문자의 엔코딩 정보
	
	결과값 : 초,중,종성으로 분할된 결과를 list로 반환
	
	"""
	global _default_encoding
	encoding = encoding or _default_encoding
	ch      = int(0)
	char    = character
	idx_cho  = int(0)
	idx_jung = int(0)
	idx_jong = int(0)
	
	return1Chr = lambda x: (x and chr(x).encode(encoding)) or str()
	return1UniChr = lambda x: (x and chr(x)) or str()
	returnCJJ = lambda x, y, z: tuple(map((type(character)==str and return1UniChr) or return1Chr, (x, y, z)))
	
	
	if type(char) == str:
		char =  char
	elif type(char) != str:
		raise TypeError("parameter type is string or unicode")
	
	ch = ord(char)
	
	# Hangul Compatibility Jamo
	#if (ch >= 0x3130 and ch <= 0x314e) or (ch >= 0x3165 and ch <= 0x3186):
	#	return returnCJJ(ch, 0, 0)
	if (ch >= 0x314f and ch <= 0x3163) or (ch >= 0x3187 and ch <= 0x318e):
		return returnCJJ(0, ch, 0)
	
	# Hangul Syllables
	if (ch >= 0xac00 and ch <= 0xd7af):
		idx_cho = int((ch - 0xac00) / 0x024c)
		idx_jung= int(((ch - 0xac00) % 0x024c) / 0x001c)
		idx_jong= int((ch - 0xac00) % 0x001c)
		return returnCJJ(getCJamoIdxChoseong(idx_cho+1)+0x3131, idx_jung+0x314f, (idx_jong and getCJamoIdxJongseong(idx_jong)+0x3131) or 0)
	
	# None
	return returnCJJ(ch, 0, 0)

###
# @brief	초/중/종성 결합 함수
# 초,중,종성을 하나의 문자로 합쳐준다.
# 주 ) splitCJJ()와 반대 개념의 함수
# 주 ) 아직까지 Hangul Jamo/옛한글 에 대한 처리는 고려하지 않았음
# 
# @param[in]		choseong	초성정보
# @param[in]		jungseong	중성정보
# @param[in]		jongseong	종성정보
# @param[in]		encoding	문자의 엔코딩 정보
#
# @return	초,중,종성을 합친 결과
###
def joinCJJ(choseong, jungseong, jongseong, encoding = None):
	""" 초/중/종성 결합 함수
	
	초,중,종성을 하나의 문자로 합쳐준다.
	주 ) splitCJJ()와 반대 개념의 함수
	주 ) 아직까지 Hangul Jamo/옛한글 에 대한 처리는 고려하지 않았음
	
	인자값 목록 (모든 변수가 반드시 필요):
	
	choseong : 초성정보
	jungseong : 중성정보
	jongseong : 종성정보
	encoding : 문자의 엔코딩 정보
	
	결과값 : 초,중,종성을 합친 결과
	
	"""
	global _default_encoding
	encoding = encoding or _default_encoding
	
	if type(choseong) == str:
		choseong = choseong
	elif type(choseong) != str:
		raise TypeError("parameter 'choseong' type is string or unicode")
	if type(jungseong) == str:
		jungseong = jungseong
	elif type(jungseong) != str:
		raise TypeError("parameter 'jungseong' type is string or unicode")
	if type(jongseong) == str:
		jongseong = jongseong
	elif type(jongseong) != str:
		raise TypeError("parameter 'jongseong' type is string or unicode")
	
	return1Chr = lambda x: (x and chr(x).encode(encoding)) or str()
	return1UniChr = lambda x: (x and chr(x)) or str()
	returnChar = lambda x: (type(choseong)==str and return1UniChr(x)) or return1Chr(x)
	
	if not jungseong:
		if not choseong:
			return returnChar(0)
		return choseong
	
	if not isCJamoChoseong(ord(choseong)):
		raise TypeError("parameter 'choseong' type is not Hangul Compatibility Choseong Jamo")
	if not isCJamoJungseong(ord(jungseong)):
		raise TypeError("parameter 'jungseong' type is not Hangul Compatibility Jungseong Jamo")
	if jongseong and (not isCJamoJongseong(ord(jongseong))):
		raise TypeError("parameter 'jungseong' type is not Hangul Compatibility Jungseong Jamo")
	
	idx_cho  = CHOSEONG_IDX_CODEMAP[ord(choseong)-0x3131]-1
	idx_jung = ord(jungseong)-0x314f
	idx_jong = (jongseong and JONGSEONG_IDX_CODEMAP[ord(jongseong)-0x3131]) or 0
	
	return returnChar(0xac00+((idx_cho*21)+idx_jung)*28+idx_jong)

###
# @brief	한글 비교 함수
# 두 문자열을 비교한다. 이는 sort 시 유용하다.
# 주 ) 기존의 cmp 로 비교하면, 문자열 코드상의 구성으로 인해
#      'ㄹ다' 등이 '가다'보다 앞에 나타나는 문제점을 보완하기 위한 함수
# 단점 ) cmp() 에 비해 처리 속도가 느리다
# 
# @param[in]		s1			비교 대상 문자열
# @param[in]		s2			비교 대상 문자열
# @param[in]		encoding	문자열 엔코딩 정보
#
# @return	s1의 문자 정보가 크면 -1, s2의 문자 정보가 크면 1, 같으면 0을 반환
###
def cmpHangul(s1, s2, encoding = None):
	""" 한글 비교 함수
	
	두 문자열을 비교한다. 이는 sort 시 유용하다.
	주 ) 기존의 cmp 로 비교하면, 문자열 코드상의 구성으로 인해
	      'ㄹ다' 등이 '가다'보다 앞에 나타나는 문제점을 보완하기 위한 함수
	단점 ) cmp() 에 비해 처리 속도가 느리다
	
	인자값 목록 (모든 변수가 반드시 필요):
	
	s1 : 비교 대상 문자열
	s2 : 비교 대상 문자열
	encoding : 문자열 엔코딩 정보
	
	결과값 : s1의 문자 정보가 크면 -1, s2의 문자 정보가 크면 1, 같으면 0을 반환
	
	"""
	global _default_encoding
	encoding = encoding or _default_encoding
	
	if type(s1) == str:
		s1 = str().join([str().join([y or str(" ") for y in splitCJJ(x)]) for x in s1])
	if type(s2) == str:
		s2 = str().join([str().join([y or str(" ") for y in splitCJJ(x)]) for x in s2])
	
	return cmp(s1, s2)

###
# @brief	한글 음가 문자 판별 함수
# 입력한 문자가 한글 음가 문자인지를 판별한다.
# isHangulChr는 음가 문자 외 다른 한글 기호도 판별 가능하나 
# 이 함수는 오로지 한글 음가 문자만을 판별한다.
# 
# @param[in]		character	문자
# @param[in]		encoding	문자의 엔코딩 정보
#
# @return	한글 음가 문자이면 True, 그렇지 않으면 False
###
def isHangulSyllable(character, encoding = None):
	""" 한글 문자 판별 함수
	
	입력한 문자가 한글 음가 문자인지를 판별한다.
	isHangulChr는 음가 문자 외 다른 한글 기호도 판별 가능하나 
	이 함수는 오로지 한글 음가 문자만을 판별한다.
	
	인자값 목록 (모든 변수가 반드시 필요):
	
	character : 문자
	encoding : 문자의 엔코딩 정보
	
	결과값 : 한글 음가 문자이면 True, 그렇지 않으면 False
	
	"""
	global _default_encoding
	encoding = encoding or _default_encoding
	
	if type(character) == str:
		character = character
	elif type(character) != str:
		raise TypeError("parameter type is string or unicode")
	return unicodedata.name(character).find("HANGUL SYLLABLE") == 0

###
# @brief	한자 음가 문자 판별 함수
# 입력한 문자가 한글 음가 문자인지를 판별한다.
# 
# @param[in]		character	문자
# @param[in]		encoding	문자의 엔코딩 정보
#
# @return	한글 음가 문자이면 True, 그렇지 않으면 False
###
def isHanjaSyllable(character, encoding = None):
	""" 한자 문자 판별 함수
	
	입력한 문자가 한자 음가 문자인지를 판별한다.
	
	인자값 목록 (모든 변수가 반드시 필요):
	
	character : 문자
	encoding : 문자의 엔코딩 정보
	
	결과값 : 한자 음가 문자이면 True, 그렇지 않으면 False
	
	"""
	global _default_encoding
	encoding = encoding or _default_encoding
	
	if type(character) == str:
		character = character
	elif type(character) != str:
		raise TypeError("parameter type is string or unicode")
	return unicodedata.name(character).find("CJK") == 0

###
# @brief	 숫자 판별 함수
# 입력한 문자가 숫자인지를 판별한다.
# 
# @param[in]		character	문자
# @param[in]		encoding	문자의 엔코딩 정보
#
# @return	숫자이면 True, 그렇지 않으면 False
###
def isNumberSyllable(character, encoding = None):
	""" 숫자 판별 함수
	
	입력한 문자가 숫자인지를 판별한다.
	
	인자값 목록 (모든 변수가 반드시 필요):
	
	character : 문자
	encoding : 문자의 엔코딩 정보
	
	결과값 : 숫자이면 True, 그렇지 않으면 False
	
	"""
	global _default_encoding
	encoding = encoding or _default_encoding
	
	if type(character) == str:
		character = character
	elif type(character) != str:
		raise TypeError("parameter type is string or unicode")
	return unicodedata.name(character).find("FULLWIDTH DIGIT") == 0 or unicodedata.name(character).find("DIGIT") == 0

###
# @brief	영어 알파벳 문자 판별 함수
# 입력한 문자가 영어 알파벳 문자인지를 판별한다.
# 
# @param[in]		character	문자
# @param[in]		encoding	문자의 엔코딩 정보
#
# @return	영어 알파벳 문자이면 True, 그렇지 않으면 False
###
def isAlphabetChr(character, encoding = None):
	""" 영어 알파벳 문자 판별 함수
	
	입력한 문자가 영어 알파벳 문자인지를 판별한다.
	
	인자값 목록 (모든 변수가 반드시 필요):
	
	character : 문자
	encoding : 문자의 엔코딩 정보
	
	결과값 : 영어 알파벳 문자이면 True, 그렇지 않으면 False
	
	"""
	global _default_encoding
	encoding = encoding or _default_encoding
	
	if type(character) == str:
		character = character
	elif type(character) != str:
		raise TypeError("parameter type is string or unicode")
	return unicodedata.name(character).find("FULLWIDTH LATIN") == 0 or unicodedata.name(character).find("LATIN") == 0

###
# @brief	기호 판별 함수
# 입력한 문자가 기호인지를 판별한다.
# 
# @param[in]		character	문자
# @param[in]		encoding	문자의 엔코딩 정보
#
# @return	기호이면 True, 그렇지 않으면 False
###
def isSymbolChr(character, encoding = None):
	""" 기호 판별 함수
	
	입력한 문자가 기호인지를 판별한다.
	
	인자값 목록 (모든 변수가 반드시 필요):
	
	character : 문자
	encoding : 문자의 엔코딩 정보
	
	결과값 : 기호이면 True, 그렇지 않으면 False
	
	"""
	global _default_encoding
	encoding = encoding or _default_encoding
	
	if type(character) == str:
		character = character
	elif type(character) != str:
		raise TypeError("parameter type is string or unicode")
	return unicodedata.category(character)[0] == "S"

###
# @brief	기호 판별 함수
# 입력한 문자가 기호인지를 판별한다.
# 
# @param[in]		character	문자
# @param[in]		encoding	문자의 엔코딩 정보
#
# @return	기호이면 True, 그렇지 않으면 False
###
def isPunctuationChr(character, encoding = None):
	""" 기호 판별 함수
	
	입력한 문자가 기호인지를 판별한다.
	
	인자값 목록 (모든 변수가 반드시 필요):
	
	character : 문자
	encoding : 문자의 엔코딩 정보
	
	결과값 : 기호이면 True, 그렇지 않으면 False
	
	"""
	global _default_encoding
	encoding = encoding or _default_encoding
	
	if type(character) == str:
		character = character
	elif type(character) != str:
		raise TypeError("parameter type is string or unicode")
	return unicodedata.category(character)[0] == "P"

###
# @brief	영어 알파벳 연결 문자 판별 함수
# 입력한 문자가 영어 알파벳의 연결 문자인지를 판별한다.
# 
# @param[in]		character	문자
# @param[in]		encoding	문자의 엔코딩 정보
#
# @return	영어 알파벳의 연결 문자이면 True, 그렇지 않으면 False
###
def isAlphabetConnectionChr(character, encoding = None):
	""" 영어 알파벳 연결 문자 판별 함수
	
	입력한 문자가 영어 알파벳의 연결 문자인지를 판별한다.
	
	인자값 목록 (모든 변수가 반드시 필요):
	
	character : 문자
	encoding : 문자의 엔코딩 정보
	
	결과값 : 영어 알파벳의 연결 문자이면 True, 그렇지 않으면 False
	
	"""
	global _default_encoding
	encoding = encoding or _default_encoding
	
	if type(character) == str:
		character = character
	elif type(character) != str:
		raise TypeError("parameter type is string or unicode")
	return character in (".", "-", "_", "|")

###
# @brief	숫자 연결 문자 판별 함수
# 입력한 문자가 숫자의 연결 문자인지를 판별한다.
# 
# @param[in]		character	문자
# @param[in]		encoding	문자의 엔코딩 정보
#
# @return	숫자의 연결 문자이면 True, 그렇지 않으면 False
###
def isNumberConnectionChr(character, encoding = None):
	""" 숫자 연결 문자 판별 함수
	
	입력한 문자가 숫자의 연결 문자인지를 판별한다.
	
	인자값 목록 (모든 변수가 반드시 필요):
	
	character : 문자
	encoding : 문자의 엔코딩 정보
	
	결과값 : 숫자의 연결 문자이면 True, 그렇지 않으면 False
	
	"""
	global _default_encoding
	encoding = encoding or _default_encoding
	
	if type(character) == str:
		character = character
	elif type(character) != str:
		raise TypeError("parameter type is string or unicode")
	return character in (".", ",")


def test():
	inputSet = ["휄","ㅁ","1","１","韓","A","Ａ", "★"]
	print("setEncoding: ", setEncoding("utf-8"))
	print("isHangulChr: ", [isHangulChr(x) for x in inputSet])
	print("splitCJJ: ", [splitCJJ(x) for x in inputSet])
	print("joinCJJ: ", [joinCJJ(*splitCJJ(x)) for x in inputSet])
	#print("cmpHangul: ", [cmpHangul(x, "가") for x in inputSet])
	print("isHangulSyllable: ", [isHangulSyllable(x) for x in inputSet])
	print("isHanjaSyllable: ", [isHanjaSyllable(x) for x in inputSet])
	print("isNumberSyllable: ", [isNumberSyllable(x) for x in inputSet])
	print("isAlphabetChr: ", [isAlphabetChr(x) for x in inputSet])
	print("isSymbolChr: ", [isSymbolChr(x) for x in inputSet])
	print("isAlphabetConnectionChr: ", [isAlphabetConnectionChr(x) for x in inputSet])
	print("isNumberConnectionChr: ", [isNumberConnectionChr(x) for x in inputSet])

if __name__ == '__main__':
	test()
