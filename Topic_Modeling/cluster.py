import numpy as np
import json
import operator
from gensim import models, corpora

# list the n documents with the highest [typ] score
# score is given by typ = {docfreq, occ, idf}
def getSignificant(typ, n):
	with open('data/%s.json' % typ, 'r') as f:
		vec = json.load(f)

	significant = dict(sorted(vec.items(), key=lambda kv: kv[1], reverse=True)[:n])

	name = 'significant_%s (n=%d).json' % (typ, n)
	with open('filtered/%s' % name, 'w') as o:
		json.dump(significant, o, sort_keys=False, indent=4)

	clean(name)

# list documents with a [typ] score >= n
# score is given by typ = {docfreq, occ, idf}
def getBaseline(typ, n):

	with open('data/%s.json' % typ, 'r') as f:
		vec = json.load(f)

	baseline = dict()

	for (doc, score) in vec.items():
		if score < n:
			continue
		baseline[doc] = score

	name = 'baseline_%s (n=%d).json' % (typ, n)
	with open('filtered/%s' % name, 'w') as o:
		json.dump(baseline, o, sort_keys=False, indent=4)


	clean(name)


# list all document citation vectors, removing any citations not included in the list given by [measure].json
#		measure = {'baseline_[typ] (n=x).json', 'significant_[typ] (n=x).json'} (or any other filtered list of documents/citations)
def clean(measure):	

	with open('filtered/%s' % measure, 'r') as f:
		filtered = json.load(f)

	with open('citations.json', 'r') as f:
		docs = json.load(f)

	cleaned = dict()

	for (doc, citations) in docs.items():

		intersection = set(citations) & set(filtered.keys())

		if len(intersection) == 0:
			continue

		cleaned[doc] = []
		print doc
		for c in citations:
			if c in set(intersection):
				cleaned[doc].append(c)

	with open('cleaned/%s' % measure, 'w') as o:
		json.dump(cleaned, o, sort_keys=True, indent=4)		


# infile = input file path
#		File must be a json file in the format of our citation graph (see README)
#
# k = number of topics
#		The LDA model represents each document as a distribution of topics with corresponding probabilities.
#		(I have had issues with values of k > 50, but don't hesitate to experiment with different values)
#
# n = number of words in each topic vector
#		The LDA model represents each topic as a distribution of words with corresponding probabilities.
#
# clean = boolean value stating whether or not we want to filter out documents with citation vectors of length < n
#
# NOTE: One thing that I have NOT tried yet is changing the number of passes the LDA model takes,
# 		mainly because I don't know what effect this will have. I recommend looking up how this might
#		affect the model, since right now the output of this model is not super accurate :/
def ldaModel(infile, k, n, clean=False):

	print "Running LDA model for %d topics..." % k

	if clean:
		typ = 'clean'
	else:
		typ = 'raw'

	with open(infile, 'r') as f:
		docs = json.load(f)

	texts = []
	docKey = dict()
	docBow = dict()
	docLen = dict()

	total = 0

	for (doc, terms) in docs.items():

		# clean=True if we are removing documents with citation vectors that are
		# less than the number of words we want to include in our topic vectors.
		if clean and len(terms) < n:
			continue

		docKey[doc] = len(texts)
		texts.append(terms)
		docLen[doc] = len(terms)


	# mean, median and mode calculations were just made for my own understanding.
	# Feel free to delete or comment this out.
	# (averages give information about citation vector LENGTHS)
	ndLen = np.array(docLen.values())
	print "MEAN   = %d" % ndLen.mean()
	print "MEDIAN = %d" % np.median(ndLen)
	print "MODE   = %d" % np.argmax(np.bincount(ndLen))


	dictionary = corpora.Dictionary(texts)
	corpus = [dictionary.doc2bow(text) for text in texts]
	ldamodel = models.ldamodel.LdaModel(corpus, num_topics=k, id2word=dictionary)

	print "LDA model created. Recording topic distributions..."

	temp = dict(ldamodel.show_topics(num_topics=k, num_words=n, formatted=False))

	topics = dict()
	bestFit = dict()

	for (topicId, probabilities) in temp.items():
		topics[topicId] = dict(probabilities)
		bestFit[topicId] = dict()

	# for each topic, we record the topic id and its word distribution vector ('word id': probability)
	# each topic should have a vector of length n
	with open('lda/%s/topics=%d words=%d TOPICS.json' % (typ, k, n), 'w') as o:
		json.dump(topics, o, sort_keys=True, indent=4)

	print "Recording document distributions..."

	docs = dict()

	for (doc, corpusId) in docKey.items():
		doc_bow = corpus[corpusId]
		doc_topics = dict(ldamodel.get_document_topics(doc_bow))

		docs[doc] = dict()

		# get max key, value pair from document topic distribution
		mk, mv = max(doc_topics.iteritems(), key=operator.itemgetter(1))

		bestFit[mk][doc] = mv
		docs[doc]['BEST FIT'] = {mk: mv}
		docs[doc]['LENGTH'] = docLen[doc]
		docs[doc]['TOPICS'] = doc_topics

	# for each document, we record the document id and
	#	LENGTH:	  The length of the document's original citation vector
	#	TOPICS:	  The topic distribution vector (given by the LDA model) for the given document
	#		  	  	('topic_id': probability)
	#	BEST FIT: The topic with the highest probability in the document's topic distribution vector (TOPICS)
	with open('lda/%s/topics=%d words=%d DOCS.json' % (typ, k, n), 'w') as o:
		json.dump(docs, o, sort_keys=True, indent=4)

	print "Done."

def main(infile, k, n):

	ldaModel(infile, k, n)
	ldaModel(infile, k, n, True)	
	

main('citations.json', 25, 5)