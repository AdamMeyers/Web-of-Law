import operator
file_num1  = 'ner_tab_EURO.txt'
file_num2  = 'termo_europal_tabbed.txt'

dic_ner={}
dictionary_overlap ={}
dic_nolap={}
with open(file_num1) as ner:
	for line in ner:
		texto = line.split('\t')
		txt = texto[0].lower()
		freq = 	texto[1]
		if txt in dic_ner:
			dic_ner[txt] += freq.strip()
		else:
			dic_ner[txt] = freq.strip()

with open(file_num2) as termo:
	for line in termo:
		texto = line.split('\t')
		txt = texto[1].lower().strip()
		freq =  texto[0]
		if txt in dic_ner:
			print(txt, dic_ner[txt], freq)
			valor_temp = dic_ner[txt]
			values_tem =  []
			values_tem.append('NER: '+valor_temp)
			values_tem.append('TERMO: '+freq)
			dictionary_overlap[txt] = values_tem

sorted_dict = sorted(dictionary_overlap.items(), key=operator.itemgetter(1), reverse=True)
with open('TERMO_NER_overlap.txt','w')as out:
	for item in sorted_dict:
		texto = item[0] + '\t' + item[1][0] + '\t' + item[1][1] + '\n'
		out.write(texto)

