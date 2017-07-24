#!/usr/bin/env python
# John Ortega - Esteban Galvis 07/20/2017
# finds terms from europarl.combine.notranslated.moses.terms in the actual sentences
# from eurolprl.eng.10000.txt and compares translation from europal.combined.es.mosest.terms to what's
# found in the ref europarl.es.10000.ref.txt
import sys
import re
import codecs

new_file='europarl.moses.found.john.txt'

# europarl.combined.notranslated.moses.terms
no_translated_terms = []
with codecs.open(sys.argv[1],'r',encoding='utf8') as ins:
    for line in ins:
        no_translated_terms.append(line.strip())

# europarl.eng.10000.txt
with codecs.open(new_file,'w',encoding='utf8') as out:
    with codecs.open(sys.argv[2],'r',encoding='utf8') as ins:
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
                    #txt = str(count)+'\t'+term+'\t'+str(match.start())+'\t'+str(match.end()) 
                    txt = str(count)+'\t'+term+'\t'+term+'\t'+str(match.start())+'\t'+str(match.end()) + '\n' 
                    out.write(txt) 
                    #no_translated_ref.append(txt)   
                    #print '$$$$$$$$$$$$$$$$$$'
            count = count +1
            #print count

