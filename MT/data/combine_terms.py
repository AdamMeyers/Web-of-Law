import sys 

terms_ner =sys.argv[1] 
terms_termo = sys.argv[2]

terms1 = [] 
terms2 = []

with open(terms_ner) as ner:
    for line in ner:
        line = line.strip()
        txt = line.split('\t')
        terms1.append(txt[0])
with open(terms_termo) as term:
    for line in term:
        line = line.strip()
        txt  = line.split('\t')
        terms2.append(txt[1])
all_terms = sorted(list(set(terms1) & set(terms2)))

for term in all_terms:
    print term
