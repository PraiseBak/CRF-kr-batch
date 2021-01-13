# -*- coding: utf-8 -*-
import json

class CRFBatch():
	dat_len = 0
	#cur_line = 0
	batch_size = 0
	iteration = 0
	feature_io = ""	
	f = ""

	def __init__(self,filename,iteration):
		self.get_file_len(filename)
		self.iteration = iteration
		self.batch_size= int(self.dat_len/self.iteration)
		self.feature_io = feature_file()

	def get_file_len(self,corpus_filename):
		self.f = open(corpus_filename,'r',encoding = 'cp949')
		while True:
			line = self.f.readline()
			if not line: 
				self.set_file_curser_front()
				break
			self.dat_len += 1

	def set_file_curser_front(self):
		self.f.seek(0)

	def return_corpus(self):
		X = list()
		Y = list()
		data = list()
		element_size = 0
		
		idx = 0
		while True:
			line = self.f.readline()
			if not line: break
			line = line.strip().split('\t')
			if len(line) is 0 or len(line) is 1:
				data.append((X,Y))
				X = list()
				Y = list()
				if idx >= self.batch_size:
					break
			else:
				if element_size is 0:
					element_size = len(line)
				elif element_size is not len(line):
					print("wrong input size")
					exit()
				X.append(line[:-1])
				Y.append(line[-1])
			idx += 1
		if len(X) > 0:
			data.append((X,Y))
		return data




class feature_file:
	feature_fw = None
	feature_fr = None
	feature_tmp_file = "feature_tmp.json"

	def __init__(self):
		self.set_feature_f()

	def init_write_file(self):
		self.feature_fw = open(self.feature_tmp_file,'w')

	def init_read_file(self):
		self.feature_fr = open(self.feature_tmp_file,'r')

	def get_feature_from_file(self):
		with open(self.feature_tmp_file,'r') as f:
			return json.load(f)['feature_dic']
			

	def set_feature_f(self):
		self.init_write_file()
		self.init_read_file()

	def result_write(self,result):
		self.init_write_file()
		json.dump(result,self.feature_fw,ensure_ascii=False,indent=4)
		self.feature_fw.flush()

	
	def get_y_dict(self,prev_y,y,feature_id):
		y_dict = str("%d_%d" % (prev_y,y))
		return y_dict


	def write_feature_into_file(self,feature_string,prev_y,y,feature_id):
		value = self.get_y_dict(prev_y,y,feature_id)
		
		try:
			with open('feature_tmp.json') as json_file:
				features = json.load(json_file)
				if not feature_string in features['feature_dic']:
					features['feature_dic'][feature_string] = dict()
				if not value in features['feature_dic'][feature_string]:
					features['feature_dic'][feature_string][value] = dict()
					features['feature_dic'][feature_string][value] = feature_id
				
				self.result_write(features)
		
		except Exception as e:
			result = dict()
			result['feature_dic']= dict()
			result['feature_dic'][feature_string]= dict()
			result['feature_dic'][feature_string][value] = dict()
			result['feature_dic'][feature_string][value] = feature_id
			self.result_write(result)




def test_code():
	import feature
	file_name = "test.txt"
	iteration = 4
	bat = CRFBatch(file_name,iteration)
	data = bat.return_corpus()
	fea = feature.FeatureSet()
	fea.scan(data,bat)

	'''
	bat.feature_io.write_feature_into_feature("U[0]=노",0,0,0)
	bat.feature_io.write_feature_into_feature("U[0]=랭",0,0,1)
	bat.feature_io.write_feature_into_feature("U[0]=이",0,0,2)
	bat.feature_io.write_feature_into_feature("U[0]=이",0,0,3)
	bat.feature_io.write_feature_into_feature("U[0]=집",1,1,4)
	bat.feature_io.write_feature_into_feature("U[0]=에",1,1,5)
	bat.feature_io.write_feature_into_feature("U[0]=온",1,1,6)
	bat.feature_io.write_feature_into_feature("U[0]=다",1,1,7)
	bat.feature_io.write_feature_into_feature("U[0]=.",1,1,8)
	bat.feature_io.write_feature_into_feature("U[0]=그",1,1,9)
	bat.feature_io.write_feature_into_feature("U[0]=볼",1,1,10)
	bat.feature_io.write_feature_into_feature("U[0]=을",1,1,11)
	bat.feature_io.write_feature_into_feature("U[0]=한",1,1,12)
	bat.feature_io.write_feature_into_feature("U[0]=번",1,1,13)
	bat.feature_io.write_feature_into_feature("U[0]=더",1,1,14)
	bat.feature_io.write_feature_into_feature("U[0]=안",1,1,15)
	bat.feature_io.write_feature_into_feature("U[0]=을",1,1,16)
	bat.feature_io.write_feature_into_feature("U[0]=수",1,1,17)
	bat.feature_io.write_feature_into_feature("U[0]=있",1,1,18)
	bat.feature_io.write_feature_into_feature("U[0]=다",1,1,19)
	bat.feature_io.write_feature_into_feature("U[0]=면",1,1,20)
	bat.feature_io.write_feature_into_feature("U[0]=.",1,1,21)
	'''
	#print("**피쳐 string 가져오기**")
	#print(bat.feature_io.get_feature_key("U[0]=엄",0,0,0))



if __name__ == "__main__":
	test_code()
