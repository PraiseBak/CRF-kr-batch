class CRFBatch():
	dat_len = 0
	#cur_line = 0
	splited_len = 0 
	batch = 0 
	f = ""
	def __init__(self,filename,batch):
		self.get_file_len(filename)
		self.batch = batch
		self.splited_len = int(self.dat_len/self.batch)
	
	def get_file_len(self,corpus_filename):
		self.f = open(corpus_filename,'r')
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
			line = line.strip().split('\t')
			if len(line) is 0 or len(line) is 1:
				data.append((X,Y))
				X = list()
				Y = list()
				if idx >= self.splited_len:
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

			







