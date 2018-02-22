import theano
import cPickle
import numpy as np
from model import BiRNN


def print_proc_bar(curr_index, total, proc_bar_width=40):
    proc = float(curr_index) / total
    proc_count = int(proc * proc_bar_width)
    print '\r[%s] %.2f%%' % ('=' * proc_count + ' ' * (proc_bar_width - proc_count), proc * 100),


def prepare_data(path_fin, batch_size, split_ratio):
    X, target = cPickle.load(open(path_fin, 'r'))

    if X.shape[0] % batch_size > 0:
        idx_to_add = np.random.choice(X.shape[0], batch_size - X.shape[0] % batch_size, replace=False)
        X = np.concatenate([X[idx_to_add], X])
        target = np.concatenate([target[idx_to_add], target])

    num_batch_train = int(X.shape[0] * split_ratio / batch_size)
    X_train = X[:num_batch_train * batch_size]
    target_train = target[:num_batch_train * batch_size]
    X_valid = X[num_batch_train * batch_size:]
    target_valid = target[num_batch_train * batch_size:]

    return X_train, target_train, X_valid, target_valid


def evaluate(pred, target):
    pred_true = target[pred == 1]
    precision = np.sum(pred_true == 1) / float(len(pred_true))

    real_true = pred[target == 1]
    recall = np.sum(real_true == 1) / float(len(real_true))

    f1_score = 2 * precision * recall / (precision + recall)

    print 'Precision: %6.2f' % (precision * 100)
    print 'Recall:    %6.2f' % (recall * 100)
    print 'F1 Score:  %6.2f' % (f1_score * 100)


def main(path_data='../data/',
         data_name='europarl-v7.es-en.en.tok.lower.dat',
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
    X_train, target_train, X_valid, target_valid = prepare_data(path_data + data_name, batch_size, split_ratio)
    print 'Done\n'

    num_batch = X_train.shape[0] / batch_size
    for e in range(nepoch):
        print 'Training in epoch %d ...' % e
        total_cost = 0
        indices = np.arange(num_batch)
        np.random.shuffle(indices)
        for curr_idx, batch_idx in enumerate(indices):
            X_batch = X_train[batch_size * batch_idx: batch_size * (batch_idx + 1)]
            target_batch = target_train[batch_size * batch_idx: batch_size * (batch_idx + 1)]
            cost = M.train(X_batch, target_batch)
            total_cost += cost
            # if verbose:
            #     print 'Batch %d: %.5f' % (batch_idx, cost)
            print_proc_bar(curr_idx + 1, num_batch)
        print '\nEpoch %d: total cost = %.5f\n' % (e, total_cost)

        print 'Predicting ...'
        prob = list()
        num_batch = X_valid.shape[0] / batch_size
        for batch_idx in range(num_batch):
            X_batch = X_valid[batch_size * batch_idx: batch_size * (batch_idx + 1)]
            prob += [M.predict(X_batch)]
            print_proc_bar(batch_idx + 1, num_batch)
        print '\nDone\n'

        prob = np.concatenate(prob)
        print 'Evaluating in epoch %d ...' % e
        evaluate(prob > 0.5, target_valid)
        print 'Done\n'

        if save_model:
            print 'Saving model ...'
            M.save(path_data + 'params' + str(e) + '.pkl')
            print 'Done\n'


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
        (params['vocab_size'], params['dim_emb'])).astype(theano.config.floatX)

    print 'Building model ...'
    M = BiRNN(params, embedding)
    print 'Done\n'

    X = np.array([[0, 4, 4, 2],
                  [1, 1, 3, 2],
                  [0, 3, 2, 0]]).astype('int32')

    target = np.array([[0, 0, 1, 0],
                       [1, 0, 0, 0],
                       [0, 1, 1, 0]]).astype('int32')

    print 'Training ...'
    for i in range(500):
        cost = M.train(X, target)
        print 'Epoch %d: %.5f' % (i, cost)
    print 'Done\n'

    print 'Predicting ...'
    prob = M.predict(X)
    print 'Done\n'

    evaluate(prob > 0.5, target)


if __name__ == '__main__':
    main()
