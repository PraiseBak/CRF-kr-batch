#!/usr/bin/env python
import sys
import argparse
from crf import LinearChainCRF
def count_args(args):
	args_keys = vars(args).keys()
	count = 0
	for key in args keys:
		if key != None:
			count+=1

	return count
if __name__ == '__main__':
	usage = "sentense inference mode: crf_kr.py \"이것은 문장입니다\"\n" 
	usage_2 = "file inference mode: crf_kr.py test_file model i False\n"
	usage_3 = "train mode : crf_kr.py train_file model train False\nyou can skip batch argument(currently batch is not executable)"

	parser = argparse.ArgumentParser(usage = '\n'+usage+usage_2+usage_3)
	parser.add_argument("input")
	parser.add_argument("--batch",'-b')
	parser.add_argument("--modelfile",'-m')
	parser.add_argument("--anwserfile",'-a')
	

		

	args = parser.parse_args()
	print(count_args(args) )
	
		
	
	exit()


	parser.add_argument("modelfile", help="model file path")
	parser.add_argument("mode",help="crf mode to execution")
	parser.add_argument("batch",help="bolean : True to use batch")
	parser.add_argument("anwserfile",nargs='?')

	args = parser.parse_args()
	

	exit()
	crf = LinearChainCRF()
	if args.mode == 'train':
		if args.batch == 'True':
			print('batch mode implement is in progress..')
			pass
		else:
			crf.train(args.data,args.modelfile,args.batch)
	

	if args.mode.startwith('i'):
		if args.batch == 'True':
			print('batch mode implement is in progress..')
			pass

		else:
			crf.only_inference(args.data,args.modelfile,args.batch)
	


	if args.mdoe == 'test':
		crf.only_inference_test(args.data,args.modelfile,args.batch)
