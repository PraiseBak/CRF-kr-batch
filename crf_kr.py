#!/usr/bin/env python
import sys
import argparse
from crf import LinearChainCRF
import utils
def count_args(args):
	args_keys = vars(args).values()
	count = 0
	for key in args_keys:
		if key != None:
			count+=1

	return count

def train(input_file,model,batch=None):
	CRF = LinearChainCRF()
	if batch == None:
		CRF.train(input_file,model)
	else:
		CRF.train(input_file,model,batch)

def inference(input_file,model):
	CRF = LinearChainCRF()
	CRF.inference_file(input_file,model)

def inference_sentense(input_sentense,model):
	CRF = LinearChainCRF()
	CRF.inference_sentense(input_sentense,model)

def test(anwser_file,input_file):
	utils.test(anwser_file,input_file)

if __name__ == '__main__':
	usage = "sentense inference mode: crf_kr.py modelfile\n" 
	usage_2 = "file inference mode: crf_kr.py test_file model -m=inference\n"
	usage_3 = "train mode : crf_kr.py -i=train_file model -m=train -b=4\n"
	usage_4 = "test mode : crf_kr.py input_file -a=anwser_file -m=test\ncurrently batch is not executable"
	parser = argparse.ArgumentParser(usage = '\n'+usage+usage_2+usage_3+usage_4)
	parser.add_argument("--input",'-i')
	parser.add_argument("model")
	parser.add_argument("--anwserfile",'-a')
	parser.add_argument("--mode",'-m')
	parser.add_argument("--batch",'-b')
	args = parser.parse_args()
	len_args = count_args(args)
	
	crf = LinearChainCRF()

	if	len_args == 1:
		print(crf.inference_sentense(args.model))
	
	elif len_args == 3 or len_args == 4 or len_args == 5:
		if args.mode == "train":
			if args.batch != None:	crf.train(args.input,args.model,args.batch)
			else: crf.train(args.input,args.model,args.batch)
		elif args.mode == "inference":	
			crf.inference_file(args.input,args.model)
		elif args.mode == "test":
			test(args.input_file,args.anwser_file)
		else:
			print("wrong args input")


	else:
		print("wrong args input")
