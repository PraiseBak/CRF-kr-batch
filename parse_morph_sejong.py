#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import glob
import re
from io import StringIO


###
# @brief	형태소 분석 정보 parsing (sejong 문서용)
# 나/NP+는/JX 로 되어 있는 것을 [('나', 'NP'), ('는', 'JX')] 로 파싱을 해준다.
#
# @param[in]		target		형태소 분석 정보 (나/NP + 는/JX)
#
# @return	파싱한 결과 : [('나', 'NP'), ('는', 'JX')]
###
def _parse_morph_sejong(target):
	import re
	
	result=list()
	buf = target
	
	loop = re.search("(\/([A-Za-z ]+)(?:\+|$))",buf)
	while loop:
		pos = buf.find(loop.group(1))
		result.append((buf[:pos].strip(), loop.group(2).strip()))
		buf = buf[pos+len(loop.group(1)):]
		loop = re.search("(\/([A-Za-z ]+)(?:\+|$))",buf)
		
	return result


