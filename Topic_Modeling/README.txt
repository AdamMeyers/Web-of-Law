Author: Anna Fenske

Web of Law - Citation Clustering using the Latent Dirichlet Allocation Model

citations.json (citation graph)
	I've stored all n documents in the graph as follows:

		{
			docId_1 : [citationId_1_1, citationId_1_2, ...],
  			... ,
  			docId_n : [citationId_n_1, citationId_n_2, ...]
		}

	The only major difference to note between this and the original citation graph is the lack of floating points distinguishing multiple references to the same cited material. That is, in the original graph, two citations to document 1001 would be marked 1001.001, 1001.002. In citations.json, these citations are simply stored as duplicate values in the same list.

data (directory)
	I've stored a few json files storing scores of each citation appearing in the citation graph.

		- docfreq.json: recorded the number of documents each citation appears in.
		- idf.json: recorded the inverse doc frequency score for each citation.
		- occ.json: recorded the total number of times each citation appears in the overall citation graph.
		- tfidf.json: recorded the tf-idf score for each citation in each document citation vector it appears in.

	I have only used idf.json and occ.json in filtering data, but I'm including all scores in case they are of any use later on.

cluster.py (python script)
	This script contains a few filtering and cleaning functions, as well as an implementation of the LDA model given by the gensim package. The ldaModel function follows the walkthrough found at https://rstudio-pubs-static.s3.amazonaws.com/79360_850b2a69980c4488b1db95987a24867a.html

lda (directory - stored results)
	So far, I have not done much by way of testing the accuracy of the model I've implemented. However, I have stored the output of gensim's LDA model run with varying values of k and n (number of topics and words per topic, respectively) in this directory.

A couple helpful links:

	- Original publication of the LDA model by Blei, Ng and Jordan
		http://ai.stanford.edu/~ang/papers/jair03-lda.pdf
	- Wikipedia entry on the LDA model
		https://en.wikipedia.org/wiki/Latent_Dirichlet_allocation
	- gensim.models.ldamodel documentation
		https://radimrehurek.com/gensim/models/ldamodel.html
