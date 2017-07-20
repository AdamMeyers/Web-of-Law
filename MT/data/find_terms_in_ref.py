#!/usr/bin/env python
# John Ortega - Esteban Galvis 07/20/2017
# finds terms from europarl.combine.notranslated.moses.terms in the actual sentences
# from eurolprl.eng.10000.txt and compares translation from europal.combined.es.mosest.terms to what's
# found in the ref europarl.es.10000.ref.txt
import sys
import re

# europarl.combined.notranslated.moses.terms
no_translated_terms = []
with open(sys.argv[1], "r") as ins:
    for line in ins:
        no_translated_terms.append(line.strip())

no_translated_ref = [] 
# europarl.eng.10000.txt
with open(sys.argv[2], "r") as ins:
    count = 1
    for line in ins:
        for term in no_translated_terms:
            the_line = line.strip()
            my_regex = r"\b(?=\w)" + re.escape(term) + r"\b(?!\w)"
            match = re.search(my_regex,the_line.lower())
            if match is not None and match.start() > -1:
                #print '------------------'
                #print "**** >>" + str(line)
                #print "**** --" + str(term) + ' '+ str(len(term))
                #print str(match.start()) + ' '+ str(match.end())
                #print '*&&^^&^&^&^ ' + str(count)
                txt = str(count)+'\t'+term+'\t'+str(match.start())+'\t'+str(match.end()) 
                no_translated_ref.append(txt)   
                #print '$$$$$$$$$$$$$$$$$$'
        count = count +1
list_en_terms = [] 
list_es_terms = [] 
#europarl.combined.en.moses.terms ins
with open(sys.argv[3], 'r') as ins:
    for line in ins:
        line_en_terms.append(line)
#europarl.combined.es.moses terms 
with open(sys.argv[4], 'r') as ins:
    for line in ins:
         line_es_terms.append(line)
with open('europarl.moses.found.txt','w') as out:
    headline = 'line number\tenglishterm\tspanishterm\tstart\tend'
    for item in no_translated_ref:
        item = item.strip()
        txt  = item.split('\t')
        line_index = list_en_terms.index(txt[1])
        list_es_terms.index(txt[1])
        if(list_en_terms == list_es_terms):
            outtxt = str(txt[0]) + '\t' + str(txt[1]) + '\t' +  str(list_es_terms[line_index])
        print outtxt
