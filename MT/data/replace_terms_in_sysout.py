#!/usr/bin/env python
# John Ortega - Esteban Galvis 07/20/2017
# expects a file with a line number, english term, and spanish term
# the spanish term will be found in the translation from moses (actually the english term because it wasn't translated)
# and replaced by the new spanish term in the tsv file sent as translation from native speakers
import sys
import re

# europarl.combined.notranslated.moses.terms
no_translated_terms = []
with open(sys.argv[1], "r") as ins:
    for line in ins:
        no_translated_terms.append(line.strip())


# europarl.eng.10000.txt
with open(sys.argv[2], "r") as ins:
    count = 1
    for line in ins:
        for term in no_translated_terms:
            the_line = line.strip()
            my_regex = r"\b(?=\w)" + re.escape(term) + r"\b(?!\w)"
            match = re.search(my_regex,the_line.lower())
            if match is not None and match.start() > -1:
                print '------------------'
                print "**** >>" + str(line)
                print "**** --" + str(term) + ' '+ str(len(term))
                print match.start()
                print '*&&^^&^&^&^ ' + str(count)
                print '$$$$$$$$$$$$$$$$$$'
        count = count +1
