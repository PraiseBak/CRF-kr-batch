#!/usr/bin/env python
import sys
import argparse
from crf import LinearChainCRF
if __name__ == '__main__':
	
	parser = argparse.ArgumentParser()
	parser.add_argument("data", help="input data file path")
	parser.add_argument("modelfile", help="model file path")
	parser.add_argument("mode",help="mode: train or test")
	parser.add_argument("batch",help="bolean : True to use batch")
	args = parser.parse_args()
				
	crf = LinearChainCRF()
	if args.mode == 'train':
		if args.batch == 'True':
			print('current not possible')
			pass
		else:
			crf.train(args.data,args.modelfile,args.batch)
	if args.mode == 'test':
		
		if args.batch == 'True':
			print('current not possible')
			pass
		else:
			crf.test(args.data,args.modelfile,args.batch)



	
