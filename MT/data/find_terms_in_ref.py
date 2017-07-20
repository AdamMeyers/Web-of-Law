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


# europarl.eng.10000.txt
with open(sys.argv[2], "r") as ins:
    for line in ins:
        for term in no_translated_terms:
            the_line = line.strip()
            if re.search(r"[^a-zA-Z]("+term+")[^a-zA-Z]", the_line).start() > 0:
                print "**** >>" + str(line)
                print "**** --" + str(term)
    

