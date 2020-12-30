#!/usr/bin/env python
import sys
import argparse
from crf import LinearChainCRF
if __name__ == '__main__':
	
	parser = argparse.ArgumentParser()
	parser.add_argument("data", help="input data file path")
	parser.add_argument("modelfile", help="model file path")
	parser.add_argument("mode",help="crf mode to execution")
	parser.add_argument("batch",help="bolean : True to use batch")
	parser.add_argument("anwserfile",nargs='?')

	args = parser.parse_args()
				
	crf = LinearChainCRF()
	if args.mode == 'train':
		if args.batch == 'True':
			print('batch mode implement is in progress..')
			pass
		else:
			crf.train(args.data,args.modelfile,args.batch)
	

	if args.mode == 'inference':
		if args.batch == 'True':
			print('batch mode implement is in progress..')
			pass
		else:
			crf.only_inference(args.data,args.modelfile,args.batch)
			

