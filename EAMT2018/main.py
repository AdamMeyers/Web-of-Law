import sys
import theano
import cPickle
import numpy as np
import pandas as pd
from model import BiRNN
from collections import OrderedDict
from sklearn.linear_model import LogisticRegression
from sklearn.externals import joblib


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


def evaluate(pred, label, idx2sys):
    n_correct = np.sum(pred == label)
    accuracy = n_correct * 100. / label.shape[0]
    print 'Total:    %d' % label.shape[0]
    print 'Correct:  %d' % n_correct
    print 'Accuracy: %.2f%%' % accuracy
    eval_table = list()
    for i in range(len(idx2sys)):
        pred_true = np.nonzero(pred == i)
        real_true = label[pred_true]
        tp = np.sum(real_true == i)
        fp = real_true.shape[0] - tp
        fn = np.sum(label == i) - tp
        tn = label.shape[0] - tp - fp - fn
        precision = 0.
        if tp + fp != 0:
            precision = tp * 100. / (tp + fp)
        recall = 0.
        if tp + fn != 0:
            recall = tp * 100. / (tp + fn)
        f1 = 0.
        if precision + recall != 0.:
            f1 = 2 * precision * recall / (precision + recall)
        eval_table += [{'System': idx2sys[i], 'TP': tp, 'FP':fp, 'TN': tn, 'FN':fn, 'Total':label.shape[0],
                        'Precision': precision, 'Recall': recall, 'F1': f1}]
    eval_table = pd.DataFrame(eval_table,
                              columns=['System', 'TP', 'FP', 'TN', 'FN', 'Total', 'Precision', 'Recall', 'F1'])
    print eval_table
    return accuracy


def predict(M, X, num_added, batch_size):
    prob = list()
    num_batch = X.shape[0] / batch_size
    for batch_idx in range(num_batch):
        X_dev_batch = X[batch_size * batch_idx: batch_size * (batch_idx + 1)]
        mask_batch = np.ones(X_dev_batch.shape, dtype=np.int32)
        mask_batch[np.nonzero(X_dev_batch == -1)] = 0
        prob += [M.predict(X_dev_batch, mask_batch)]
        # if verbose and batch_idx % 100 == 0:
        #     print 'Batch %d' % (batch_idx)
        #     sys.stdout.flush()
        # print_proc_bar(batch_idx + 1, num_batch)
    return np.concatenate(prob)[num_added:]


def nn(path_data='../data/',
       path_params=None,
       batch_size=50,
       max_len=100,
       dim_hidden=300,
       lr=0.025,
       nepoch=20,
       verbose=True,
       save=True,
       file_scores=OrderedDict([('moses', 'es.2016.omega.tm.score.moses.pkl'),
                                ('apertium', 'es.2016.omega.tm.score.apertium.pkl'),
                                ('nematus', 'es.2016.omega.tm.score.nematus.pkl'),
                                 ('opennmt', 'es.2016.omega.tm.score.opennmt.pkl')])):
    print 'Loading word embeddings ...'
    embedding = cPickle.load(open(path_data + 'embedding.pkl', 'r'))
    embedding = embedding.astype(theano.config.floatX)
    print 'Done', '\n'

    idx2sys = {idx: syst for idx, syst in enumerate(file_scores.keys())}
    params = {
        'batch_size': batch_size,
        'max_len': max_len,
        'vocab_size': embedding.shape[0],
        'dim_emb': embedding.shape[1],
        'dim_hidden': dim_hidden,
        'n_classes': len(idx2sys),
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
    X_train= cPickle.load(open(path_data + 'X_train.pkl', 'r'))
    X_dev = cPickle.load(open(path_data + 'X_dev.pkl', 'r'))
    X_test = cPickle.load(open(path_data + 'X_test.pkl', 'r'))

    Y_train = cPickle.load(open(path_data + 'Y_train.pkl', 'r'))
    Y_dev = cPickle.load(open(path_data + 'Y_dev.pkl', 'r'))
    Y_test = cPickle.load(open(path_data + 'Y_test.pkl', 'r'))

    X_train, Y_train, _ = add_extra(batch_size, X_train, Y_train)
    X_dev, _, num_added_dev = add_extra(batch_size, X_dev)
    X_test, _, num_added_test = add_extra(batch_size, X_test)
    print 'Done\n'

    best_accuracy = 0.
    count_no_improv = 0
    e = -1
    while True:
        e += 1
        print 'Training in epoch %d ...' % e
        total_cost = 0
        num_batch_train = X_train.shape[0] / batch_size
        indices = np.arange(num_batch_train)
        np.random.shuffle(indices)
        for curr_idx, batch_idx in enumerate(indices):
            X_train_batch = X_train[batch_size * batch_idx: batch_size * (batch_idx + 1)]
            mask_train_batch = np.ones(X_train_batch.shape, dtype=np.int32)
            mask_train_batch[np.nonzero(X_train_batch == -1)] = 0
            Y_train_batch = Y_train[batch_size * batch_idx: batch_size * (batch_idx + 1)]
            cost = M.train(X_train_batch, mask_train_batch, Y_train_batch)
            total_cost += cost
            # if verbose and curr_idx % 100 == 0:
            #     print 'Batch %d: %.5f' % (curr_idx, cost)
            #     sys.stdout.flush()
            # print_proc_bar(curr_idx + 1, num_batch_train)
        print '\nEpoch %d: total cost = %.5f\n' % (e, total_cost)

        print 'Predicting on dev in epoch %d ...' % e
        prob_dev = predict(M, X_dev, num_added_dev, batch_size)
        print '\nDone\n'

        print 'Evaluating on dev in epoch %d ...' % e
        accuracy = evaluate(np.argmax(prob_dev, axis=1), Y_dev, idx2sys)
        print 'Done\n'

        print 'Predicting on test in epoch %d ...' % e
        prob_test = predict(M, X_test, num_added_test, batch_size)
        print '\nDone\n'

        print 'Evaluating on test in epoch %d ...' % e
        evaluate(np.argmax(prob_test, axis=1), Y_test, idx2sys)
        print 'Done\n'

        if accuracy > best_accuracy:
            best_accuracy = accuracy
            count_no_improv = 0
            print 'New best epoch: %d\n' % e

            if save and e > 0:
                print 'Saving predictions ...'
                cPickle.dump(prob_dev, open(path_data + 'params/BiRNN/prob_dev_' + str(e) + '.pkl', 'w'))
                cPickle.dump(prob_test, open(path_data + 'params/BiRNN/prob_test_' + str(e) + '.pkl', 'w'))
                print 'Done\n'

                print 'Saving model ...'
                M.save(path_data + 'params/BiRNN/epoch' + str(e) + '.pkl')
                print 'Done\n'

        else:
            count_no_improv += 1

        sys.stdout.flush()

        if count_no_improv > 10:
            break


def clf(path_data='../data/',
        data_type='BOW',
        clf_name='LogisticRegression',     # 'SVC' or 'LogisticRegression'
        verbose=True,
        save=True,
        file_scores=OrderedDict([('moses', 'es.2016.omega.tm.score.moses.pkl'),
                                 ('apertium', 'es.2016.omega.tm.score.apertium.pkl'),
                                 ('nematus', 'es.2016.omega.tm.score.nematus.pkl'),
                                 ('opennmt', 'es.2016.omega.tm.score.opennmt.pkl')])):
    print 'Preparing data ...'
    X_train = joblib.load(path_data + 'X_' + data_type + '_train.pkl')
    X_dev = joblib.load(path_data + 'X_' + data_type + '_dev.pkl')
    X_test = joblib.load(path_data + 'X_' + data_type + '_test.pkl')

    Y_train = cPickle.load(open(path_data + 'Y_train.pkl', 'r'))
    Y_dev = cPickle.load(open(path_data + 'Y_dev.pkl', 'r'))
    Y_test = cPickle.load(open(path_data + 'Y_test.pkl', 'r'))

    idx2sys = {idx: syst for idx, syst in enumerate(file_scores.keys())}
    print 'Done\n'

    print 'Fitting model ...'
    max_iter = -1 if clf_name == 'SVC' else 500
    model = eval(clf_name)(verbose=verbose, max_iter=max_iter)
    model.fit(X_train, Y_train)
    print 'Done\n'

    print 'Evaluating on dev set ...'
    pred_dev = model.predict(X_dev)
    evaluate(pred_dev, Y_dev, idx2sys)
    print 'Done\n'

    print 'Evaluating on test set ...'
    pred_test = model.predict(X_test)
    evaluate(pred_test, Y_test, idx2sys)
    print 'Done\n'

    if save:
        print 'Saving predictions ...'
        cPickle.dump(pred_dev, open(path_data + 'params/' + clf_name + '/' + data_type + '_pred_dev.pkl', 'w'))
        cPickle.dump(pred_test, open(path_data + 'params/' + clf_name + '/' + data_type + '_pred_test.pkl', 'w'))
        print 'Done\n'

        print 'Saving model ...'
        joblib.dump(model, path_data + 'params/' + clf_name + '/' + data_type + '_model.pkl')
        print 'Done\n'


if __name__ == '__main__':
    nn()
    # clf()
