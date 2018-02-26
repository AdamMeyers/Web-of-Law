import sys
import theano
import cPickle
import numpy as np
from model import BiRNN


def print_proc_bar(curr_index, total, proc_bar_width=40):
    proc = float(curr_index) / total
    proc_count = int(proc * proc_bar_width)
    print '\r[%s] %.2f%%' % ('=' * proc_count + ' ' * (proc_bar_width - proc_count), proc * 100),


def add_extra(X_train, Y_train, X_test, Y_test, batch_size):
    if X_train.shape[0] % batch_size > 0:
        idx_to_add = np.random.choice(X_train.shape[0], batch_size - X_train.shape[0] % batch_size, replace=False)
        X_train = np.concatenate([X_train[idx_to_add], X_train])
        Y_train = np.concatenate([Y_train[idx_to_add], Y_train])

    num_added = 0
    if X_test.shape[0] % batch_size > 0:
        num_added = batch_size - X_test.shape[0] % batch_size
        X_test = np.concatenate([X_test[:num_added], X_test])

    return X_train, Y_train, X_test, Y_test, num_added


def prepare_data1(path_fin, batch_size, split_ratio):
    X, Y = cPickle.load(open(path_fin, 'r'))

    num_train = int(X.shape[0] * split_ratio)
    X_train = X[:num_train]
    Y_train = Y[:num_train]
    X_test = X[num_train:]
    Y_test = Y[num_train:]

    # print 'Dumping test data ...'
    # cPickle.dump([X_test, Y_test], open(path_fin + '.test', 'w'))
    # print 'Done\n'

    return add_extra(X_train, Y_train, X_test, Y_test, batch_size)


def prepare_data2(data_train_name, data_test_name, batch_size):
    X_train, Y_train = cPickle.load(open(data_train_name, 'r'))
    X_test, Y_test = cPickle.load(open(data_test_name, 'r'))
    return add_extra(X_train, Y_train, X_test, Y_test, batch_size)


def evaluate(pred, target):
    pred_true = target[np.nonzero(pred == 1)]
    precision = np.sum(pred_true == 1) / float(len(pred_true))

    real_true = pred[np.nonzero(target == 1)]
    recall = np.sum(real_true == 1) / float(len(real_true))

    f1_score = 2 * precision * recall / (precision + recall)

    print 'Precision: %6.2f' % (precision * 100)
    print 'Recall:    %6.2f' % (recall * 100)
    print 'F1 Score:  %6.2f' % (f1_score * 100)


def main(path_data='/scratch/wl1191/MTEuroparl/data/wikipedia/',
         data_name='europarl-v7.es-en.en.tok.lower.dat',
         data_train_name=None,  # '/scratch/wl1191/MTEuroparl/data/wikipedia/enwiki-20140707-corpus.articles.tok.lower.dat',
         data_test_name=None,   # '/scratch/wl1191/MTEuroparl/data/europarl/europarl-v7.es-en.en.tok.lower.dat.test',
         path_params=None,
         split_ratio=0.8,
         batch_size=50,
         max_len=50,
         dim_hidden=300,
         grad_clip=100,
         lr=0.01,
         nepoch=5,
         verbose=True,
         save_model=True):
    print 'Loading word embeddings ...'
    embedding = cPickle.load(open(path_data + 'embedding.pkl', 'r'))
    print 'Done', '\n'

    params = {
        'batch_size': batch_size,
        'max_len': max_len,
        'vocab_size': embedding.shape[0],
        'dim_emb': embedding.shape[1],
        'dim_hidden': dim_hidden,
        'grad_clip': grad_clip,
        'lr': lr
    }

    print 'Building model ...'
    M = BiRNN(params, embedding)
    print 'Done\n'

    if path_params is not None:
        print 'Loading model ...'
        M.load(path_params)
        print 'Done\n'

    print 'Preparing data ...'
    if data_name is not None:
        X_train, Y_train, X_test, Y_test, num_added = prepare_data1(path_data + data_name, batch_size, split_ratio)
    else:
        X_train, Y_train, X_test, Y_test, num_added = prepare_data2(data_train_name, data_test_name, batch_size)
    print 'Done\n'

    num_batch = X_train.shape[0] / batch_size
    for e in range(nepoch):
        print 'Training in epoch %d ...' % e
        total_cost = 0
        indices = np.arange(num_batch)
        np.random.shuffle(indices)
        for curr_idx, batch_idx in enumerate(indices):
            X_train_batch = X_train[batch_size * batch_idx: batch_size * (batch_idx + 1)]
            Y_train_batch = Y_train[batch_size * batch_idx: batch_size * (batch_idx + 1)]
            cost = M.train(X_train_batch, Y_train_batch)
            total_cost += cost
            if verbose and curr_idx % 100 == 0:
                print 'Batch %d: %.5f' % (curr_idx, cost)
                sys.stdout.flush()
            # print_proc_bar(curr_idx + 1, num_batch)
        print '\nEpoch %d: total cost = %.5f\n' % (e, total_cost)

        print 'Predicting ...'
        prob = list()
        num_batch = X_test.shape[0] / batch_size
        for batch_idx in range(num_batch):
            X_test_batch = X_test[batch_size * batch_idx: batch_size * (batch_idx + 1)]
            prob += [M.predict(X_test_batch)]
            if verbose and batch_idx % 100 == 0:
                print 'Batch %d' % (batch_idx)
                sys.stdout.flush()
            # print_proc_bar(batch_idx + 1, num_batch)
        print '\nDone\n'

        prob = np.concatenate(prob)[num_added:]
        print 'Evaluating in epoch %d ...' % e
        evaluate(prob > 0.5, Y_test)
        print 'Done\n'

        if save_model:
            print 'Saving model ...'
            M.save(path_data + 'params/epoch' + str(e) + '.pkl')
            print 'Done\n'

        sys.stdout.flush()


def toy():
    params = {
        'batch_size': 3,
        'max_len': 4,
        'vocab_size': 5,
        'dim_emb': 6,
        'dim_hidden': 3,
        'grad_clip': 100,
        'lr': 0.01
    }
    embedding = np.arange(params['vocab_size'] * params['dim_emb']).reshape(
        (params['vocab_size'], params['dim_emb'])
    ).astype(theano.config.floatX)

    print 'Building model ...'
    M = BiRNN(params, embedding)
    print 'Done\n'

    X = np.array([[0, 4, 4, 2],
                  [1, 1, 3, 2],
                  [0, 3, 2, 0]]).astype('int32')

    Y = np.array([[0, 0, 1, 0],
                  [1, 0, 0, 0],
                  [0, 1, 1, 0]]).astype('int32')

    print 'Training ...'
    for i in range(500):
        cost = M.train(X, Y)
        print 'Epoch %d: %.5f' % (i, cost)
    print 'Done\n'

    print 'Predicting ...'
    prob = M.predict(X)
    print 'Done\n'

    evaluate(prob > 0.5, Y)


if __name__ == '__main__':
    main()
