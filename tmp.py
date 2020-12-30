
def word_to_eumjeol():
	
	filename = "10000test.dat"
	with open(filename,'r',encoding='utf-8') as f:
		dat = f.readlines()
	sentense = list()
	for line in dat:
		sentense.append(line.split('\t')[0])
	

	with open("10000test.um",'w') as f2:
		for line in sentense:
			if not line == '\n':
				f2.write(line+'\n')
			else:
				f2.write('\n')
	
def eumjeol_to_sentense():
	filename = "10000test.um"

	with open(filename,'r',encoding="utf-8") as f:
		data = f.readlines()
		lines = ""
		sentenses = list()
		for line in data:
			if line == "\n":
				sentenses.append(lines.rstrip(' '))
				lines= ""
				continue
			else:
				lines += (line + ' ').replace('\n','')
	output = "10000test.sentense"

	
	with open(output,'w') as f2:
		for sentense in sentenses:
			f2.write(sentense+'\n')

if __name__ == "__main__":
	eumjeol_to_sentense()
