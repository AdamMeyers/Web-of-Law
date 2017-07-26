#!/usr/bin/env python
# John Ortega - Esteban Galvis 07/20/2017
# expects a file with a line number, english term, and spanish term
# the spanish term will be found in the translation from moses (actually the english term because it wasn't translated)
# and replaced by the new spanish term in the tsv file sent as translation from native speakers
import sys
import re
import codecs

new_file = 'test.test.europarl.es.10000.moses.lc.replaced.txt'

base_moses_sentences = []
# gather all lines in a list
# europarl.es.10000.moses.txt
# process Unicode text
with codecs.open(sys.argv[1],'r',encoding='utf8') as f:
    for line in f:
        new_line = line.strip()
        base_moses_sentences.append(new_line)

# gather edit positions in a dict
# europarl.moses.found.txt
# process Unicode text
lines_with_terms_and_positions = {}
with codecs.open(sys.argv[2],'r',encoding='utf8') as f:
    for line in f:
        new_line = line.strip()
        tab_line = new_line.split('\t')
        line_number = tab_line[0]
        eng_term    = tab_line[1]
        sp_term     = tab_line[2]
        pos_start   = tab_line[3]
        pos_end     = tab_line[4]
        # assign spanish text with pos start
        # to be inserted in new file
        if eng_term == sp_term:
            lines_with_terms_and_positions[line_number] = (eng_term,pos_start,pos_end)

## create new utf-8 file with replaced translations
## now we go through the human translated terms and replace in file
## europarl.es.humantranslated.tsv
human_translated_terms = {}
with codecs.open(sys.argv[3],'r',encoding='utf8') as f:
    for line in f:
        new_line = line.strip()
        tab_line = new_line.split('#%#')
        eng_term    = tab_line[0]
        sp_term     = tab_line[1]
        human_translated_terms[eng_term] = sp_term


## now we have a dictionary with new term replacements
## get original file and replace
with codecs.open(new_file,'w',encoding='utf8') as final:
    counter =1
    for sent in base_moses_sentences:
        newsent = sent
        if unicode(str(counter),"utf-8") in lines_with_terms_and_positions:
            tpl = lines_with_terms_and_positions[unicode(str(counter),"utf-8")]
            eng_term  = tpl[0]
            pos_start = tpl[1]
            pos_end   = tpl[2]
            if eng_term in human_translated_terms:
                # replace with new spanish term
                print counter
                #There is a bug that doesnt find an index eng_word, this is because it is june 1998 and 
                #the translated text by moses outputs it 1998 aldana june
                if eng_term in newsent:
                    new_index_start  = newsent.index(eng_term) 
                    new_index_end    = new_index_start + len(eng_term)
                    newsent = newsent[0:int(new_index_start)] + ' ' + human_translated_terms[eng_term] + ' '+ newsent[int(new_index_end)+1:]
        final.write(newsent)
        final.write('\n')
        counter = counter + 1
final.close()









