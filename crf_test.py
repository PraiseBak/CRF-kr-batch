#!/usr/bin/env python

import argparse
from crf import LinearChainCRF

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("datafile", help="data file for testing input")
	parser.add_argument("modelfile", help="the model file name.")

	test_datafile = "TEST2.txt"
	test_model = "new_model.json"
	import os
	import sys
	import time
	test_datafile= os.path.join(os.path.dirname(os.path.realpath(__file__)))+'/small_test.data'
	
	test_model = os.path.join(os.path.dirname(os.path.realpath(__file__)))+'/small_model.json'


	crf = LinearChainCRF()
	model_load_start = time.time()
	crf.load(test_model)
	print("로드 시간 = ",time.time() - model_load_start)
	
	crf.test(test_datafile)
	print(time.time() - model_load_start)
