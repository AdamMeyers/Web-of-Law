import cPickle
import numpy as np


def train_w2v(path_data, file_name, dim_emb):
    import gzip
    from word2vec import word2vec

    embedder, dictionary = word2vec(
        # List of files comprising the corpus
        files=[path_data + file_name],
        # directory in which to save embedding parameters (deepest dir created if doesn't exist)
        save_dir=path_data,
        num_processes=4,
        # Number of passes through training corpus
        num_epochs=10,
        # Size of minibatches during training
        batch_size=1000,
        # Number of "noise" examples included for every "signal" example
        noise_ratio=15,
        # Dimensionality of the embedding vector space
        num_embedding_dimensions=dim_emb,
        # Print messages during training
        verbose=True
    )

    print 'Dumping ...'
    # Save word embeddings
    npfile = np.load(path_data + '/embeddings.npz')
    W = npfile['W'].astype('float32')
    emb_padding = np.zeros(shape=(1, dim_emb)).astype('float32')
    emb_not_aplha = np.random.uniform(-1. / dim_emb, 1. / dim_emb, size=(1, dim_emb)).astype('float32')
    embedding = np.concatenate([emb_padding, emb_not_aplha, W])
    cPickle.dump(embedding, open(path_data + '/embedding.pkl', 'w'))

    # Save word-to-index map
    word2idx = {'#####': 0, '#NOT_ALPHA#': 1}
    fin = gzip.open(path_data + '/dictionary/token-map.gz')
    for index, line in enumerate(fin):
        w = line.rstrip('\r\n')
        word2idx[w] = index + 2
    cPickle.dump(word2idx, open(path_data + '/word2idx.pkl', 'w'))
    print 'Done\n'


def get_nearest(word2idx, idx2word, embedding, w, n):
    w = w.lower()
    print 'Finding words nearest to %s ...\n' % w
    if w not in word2idx:
        print 'Error: \'%s\' not found in the vocab' % w
        return

    if n > len(word2idx) - 1:
        n = len(word2idx) - 1

    wid = [word2idx[w]]
    v_w = embedding[wid]

    dot_prod = np.sum(v_w * embedding, axis=1)
    norm_v_w = np.sqrt(np.sum(v_w ** 2))
    norm_emb = np.sqrt(np.sum(embedding ** 2, axis=1))
    score = dot_prod / (norm_v_w * norm_emb)

    top_indices = np.argsort(score * -1)[1: n+1]
    top_w = [idx2word[wid] for wid in top_indices]

    print 'Top %d words nearest to %s:' % (n, w)
    print ', '.join(top_w), '\n'


def main(path_data='/scratch/wl1191/MTEuroparl/data/europarl/',
         file_name='enwiki-20140707-corpus.articles.tok.lower',
         dim_emb=300):
    # train_w2v(path_data, file_name, dim_emb)
    import gzip

    print 'Dumping ...'
    # Save word embeddings
    npfile = np.load(path_data + '/embeddings.npz')
    W = npfile['W'].astype('float32')
    emb_padding = np.zeros(shape=(1, dim_emb)).astype('float32')
    emb_not_aplha = np.random.uniform(-1. / dim_emb, 1. / dim_emb, size=(1, dim_emb)).astype('float32')
    embedding = np.concatenate([emb_padding, emb_not_aplha, W])
    cPickle.dump(embedding, open(path_data + '/embedding.pkl', 'w'))

    # Save word-to-index map
    word2idx = {'#####': 0, '#NOT_ALPHA#': 1}
    fin = gzip.open(path_data + '/dictionary/token-map.gz')
    for index, line in enumerate(fin):
        w = line.rstrip('\r\n')
        word2idx[w] = index + 2
    cPickle.dump(word2idx, open(path_data + '/word2idx.pkl', 'w'))
    print 'Done\n'

    # print 'Loading data ...'
    # word2idx = cPickle.load(open(path_data + 'word2idx.pkl', 'r'))
    # embedding = cPickle.load(open(path_data + 'embedding.pkl', 'r'))
    # idx2word = dict([(v, k) for k, v in word2idx.iteritems()])
    # print 'Done', '\n'
    #
    # while True:
    #     w = raw_input('Enter a word (enter \'q\' to quit): ')
    #     if w == 'q':
    #         break
    #     get_nearest(word2idx, idx2word, embedding, w, 10)


if __name__ == '__main__':
    main()
