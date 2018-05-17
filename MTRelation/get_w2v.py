import gensim
import cPickle
import numpy as np


class DocIterator:
    def __init__(self, path_doc):
        self.path_doc = path_doc

    def __iter__(self):
        with open(self.path_doc, 'r') as fin:
            for line in fin:
                yield line.split(' ')


def train(path_doc='/scratch/wl1191/MTScore/data/es.2016.omega.tm',
          path_out='../data/',
          suffix='es',
          dim_emb=300):
    print 'Generating word vectors ...\n'
    model = gensim.models.Word2Vec(DocIterator(path_doc), size=dim_emb, min_count=5, iter=3, workers=2)
    wv = model.wv
    del model
    print '\nDone\n'

    print 'Writing out ...'
    word2idx = {'UNK': 0}
    embedding = [np.random.randn(dim_emb)]
    for idx, w in enumerate(wv.vocab):
        word2idx[w] = idx
        embedding += [wv[w]]
    word2idx['PADDING'] = len(word2idx)
    embedding += [np.zeros(dim_emb)]
    embedding = np.stack(embedding)
    cPickle.dump(word2idx, open(path_out + 'word2idx_' + suffix +'.pkl', 'w'))
    cPickle.dump(embedding, open(path_out + 'embedding_' + suffix + '.pkl', 'w'))
    print 'Done\n'

    print 'Embedding shape', embedding.shape


if __name__ == '__main__':
    train()
