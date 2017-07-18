import glob
import os 
import xml.etree.ElementTree
files = 'acquis_formal/es/train_es/*'
lines = [] 
for dire in glob.glob(files):
	for _file in os.listdir(dire):
		name_file = dire + '/' + _file
		with open(name_file) as archivo:
			e = xml.etree.ElementTree.parse(name_file).getroot()
			for line in e.itertext():
				line = line.lower()
				lines.append(line.strip())

with open('train_es_aquis.txt','w') as out:
	for line in lines:
		out.write(line + '\n')

