import sys
import theano
import cPickle
import numpy as np
from model import BiRNN


def print_proc_bar(curr_index, total, proc_bar_width=40):
    proc = float(curr_index) / total
    proc_count = int(proc * proc_bar_width)
    print '\r[%s] %.2f%%' % ('=' * proc_count + ' ' * (proc_bar_width - proc_count), proc * 100),


def add_extra(batch_size, X, Y=None):
    num_added = 0
    if X.shape[0] % batch_size > 0:
        num_added = batch_size - X.shape[0] % batch_size
        idx_to_add = np.random.choice(X.shape[0], num_added, replace=False)
        X = np.concatenate([X[idx_to_add], X])
        if Y is not None:
            Y = np.concatenate([Y[idx_to_add], Y])
    return X, Y, num_added


def evaluate(pred, target):
    pred_true = target[np.nonzero(pred == 1)]
    precision = np.sum(pred_true == 1) / float(len(pred_true))

    real_true = pred[np.nonzero(target == 1)]
    recall = np.sum(real_true == 1) / float(len(real_true))

    f1_score = 2 * precision * recall / (precision + recall)

    print 'Precision: %6.2f' % (precision * 100)
    print 'Recall:    %6.2f' % (recall * 100)
    print 'F1 Score:  %6.2f' % (f1_score * 100)


def main(path_data='../data/wikipedia/',
         data_train_name='enwiki-20140707-corpus.articles.tok.lower.numbered.train.50.dat',
         data_dev_name={
             'euro': 'europarl-v7.es-en.en.tok.lower.numbered.dev.50.dat',
             'wiki': 'enwiki-20140707-corpus.articles.tok.lower.numbered.dev.50.dat'
         },
         path_params=None,
         batch_size=50,
         max_len=50,
         dim_hidden=300,
         grad_clip=100,
         lr=0.025,
         nepoch=3,
         verbose=True,
         save=True):
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
    X_train, Y_train = cPickle.load(open(path_data + data_train_name, 'r'))
    X_train, Y_train, _ = add_extra(batch_size, X_train, Y_train)
    data_dev = dict()
    for dat in data_dev_name:
        X_dev, Y_dev = cPickle.load(open(path_data + data_dev_name[dat], 'r'))
        X_dev, _, num_added = add_extra(batch_size, X_dev, Y_dev)
        data_dev[dat] = {'X': X_dev, 'Y': Y_dev, 'num_added': num_added}
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

        for dat in data_dev:
            print 'Predicting on %s ...' % dat
            prob = list()
            num_batch = data_dev[dat]['X'].shape[0] / batch_size
            for batch_idx in range(num_batch):
                X_dev_batch = data_dev[dat]['X'][batch_size * batch_idx: batch_size * (batch_idx + 1)]
                prob += [M.predict(X_dev_batch)]
                if verbose and batch_idx % 100 == 0:
                    print 'Batch %d' % (batch_idx)
                    sys.stdout.flush()
                # print_proc_bar(batch_idx + 1, num_batch)
            print '\nDone\n'

            prob = np.concatenate(prob)[data_dev[dat]['num_added']:]
            print 'Evaluating in epoch %d ...' % e
            evaluate(prob > 0.5, data_dev[dat]['Y'])
            print 'Done\n'

            if save:
                print 'Saving predictions ...'
                cPickle.dump(prob, open(path_data + 'params/prob_' + dat + str(e) + '.pkl', 'w'))
                print 'Done\n'

        if save:
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
