class CRFBatch():
	dat_len = 0
	#cur_line = 0
	splited_len = 0 
	batch = 0 
	f = ""
	def __init__(self,filename,batch):
		self.get_file_len(filename)
		self.batch = batch
		self.splited_len = self.dat_len/self.batch
	
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

	def return_corpus():
		for i in range(self.splited_len):
			line = self.f.readline()
			







