#!/usr/bin/env python
import sys
import argparse
from crf import LinearChainCRF
def count_args(args):
	args_keys = vars(args).values()
	count = 0
	for key in args_keys:
		if key != None:
			count+=1

	return count
if __name__ == '__main__':
	usage = "sentense inference mode: crf_kr.py \"이것은 문장입니다\" modelfile\n" 
	usage_2 = "file inference mode: crf_kr.py test_file model -batch=False -mode=inference -a=anwser.txt -\n"
	usage_3 = "train mode : crf_kr.py train_file model train False\nyou can skip batch argument(currently batch is not executable)"

	parser = argparse.ArgumentParser(usage = '\n'+usage+usage_2+usage_3)
	parser.add_argument("input")
	parser.add_argument("model")
	parser.add_argument("--batch",'-b')
	parser.add_argument("--anwserfile",'-a')
	parser.add_argument("--mode",'-m')
	args = parser.parse_args()
	len_args = count_args(args)
	
	
	crf = LinearChainCRF()
	print(len_args)	
	print(len_args == 2)
	if len_args == 3 or len_args == 2:
		if args.batch == None:
			args.batch = False

		crf.inference_sentense(args.input,args.model,args.batch)
	
	elif len_args == 4 or len_args == 5:
		if args.mode == "train":
			if args.batch == 'True':
				print('batch mode implement is in progress..')
			else:

				crf.train(args.data,args.modelfile,args.batch)
		else:
			if args.batch == 'True':
				
				print('batch mode implement is in progress..')

			else:

				crf.only_inference(args.data,args.modelfile,args.batch)

	elif args.mode == 'test':
		crf.only_inference_test(args.data,args.modelfile,args.batch)
