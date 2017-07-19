
#This script is to parse the output file of Stanford's NER when the output
#format is tabbedEntities

import operator
file_name = '../NER_europal.tsv'
counter = 0
dictionary = {} 
 
with open(file_name) as archivo:
	for line in archivo:
		texto = line.strip()
		text  = texto.split('\t')		
		if len(text) >1:
		#	print ( text[0] + ' : '+ text[1])
			key = text[0] 
			if key in dictionary:
				dictionary[key] +=1 
			else:
				dictionary[key] = 1
sorted_dict = sorted(dictionary.items(), key=operator.itemgetter(1), reverse=True)
#print (sorted_dict)
with open('ner_tab_EURO.tsv','w') as out:
	for item in sorted_dict:
		out.write(str(item[0])+'\t'+str(item[1])+'\n')
