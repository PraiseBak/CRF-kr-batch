class CRFBatch():
	dat_len = 0
	current_line = 0
	splited_len = 0 
	batch = 0 
	f = ""
	def __init__(self,filename,batch):
		self.get_file_len(filename)
		self.batch = batch
		self.splited_len = self.dat_len/batch
	def get_file_len(self,corpus_filename):
		self.f = open(corpus_filename,'r')
		while True:
			line = self.f.readline()
			if not line: 
				self.f.seek(0)
				break
			self.dat_len += 1
	






