
files = [] 

archivo = 'train_es_aquis.txt' 
def readFile(_file):
	with open(_file,'r') as archivo , open('clean_train_es_acquis.txt','w') as newFile:
		for line in archivo:
			if line.strip():
				newFile.write(line.strip() + '\n')
	newFile.close()
readFile(archivo)		
		
