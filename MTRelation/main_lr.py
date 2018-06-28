import os
import sys
import cPickle
import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.externals import joblib
from sklearn.linear_model import LogisticRegression


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


def clf(path_data='/misc/proteus1/data/jortega/Web-of-Law/MT/MTRelation/data/',
        mode='each3',    # 'prev', 'all', 'top3', or 'each3'
        data_type='en_Tfidf5',    # 'en_Tfidf', 'en_Tfidf5', or 'en-es_Tfidf5'
        clf_name='LogisticRegression',
        balance=False,
        verbose=True,
        save=True):
    if mode == 'prev':
        mt_systems = ['moses', 'apertium', 'nematus']
    elif mode == 'all':
        mt_systems = ['moses', 'apertium', 'nematus', 'opennmt', 'cdec']
    elif mode == 'top3':
        mt_systems = ['nematus', 'opennmt', 'cdec']
    else:
        mt_systems = ['nematus', 'cdec', 'apertium']

    print 'Preparing data ...'
    if data_type.startswith('en-es'):
        dt = data_type.split('_')[-1]
        X_train = sparse.hstack(
            [joblib.load(path_data + 'X_' + syst + '_' + dt + '_train.pkl') for syst in ['en'] + mt_systems],
            format='csr'
        )
        X_dev = sparse.hstack(
            [joblib.load(path_data + 'X_' + syst + '_' + dt + '_dev.pkl') for syst in ['en'] + mt_systems],
            format='csr'
        )
        X_test = sparse.hstack(
            [joblib.load(path_data + 'X_' + syst + '_' + dt + '_test.pkl') for syst in ['en'] + mt_systems],
            format='csr'
        )
    else:
        X_train = joblib.load(path_data + 'X_' + data_type + '_train.pkl')
        X_dev = joblib.load(path_data + 'X_' + data_type + '_dev.pkl')
        X_test = joblib.load(path_data + 'X_' + data_type + '_test.pkl')

    Y_train = cPickle.load(open(path_data + mode + '/Y_train.pkl', 'r'))
    Y_dev = cPickle.load(open(path_data + mode + '/Y_dev.pkl', 'r'))
    Y_test = cPickle.load(open(path_data + mode + '/Y_test.pkl', 'r'))
    print 'Done\n'

    if balance:
        print 'Balancing data ...'
        syst_indices = [np.nonzero(Y_train == i)[0] for i in range(len(mt_systems))]
        n = np.min([len(si) for si in syst_indices])
        syst_indices = np.concatenate([np.random.choice(si, n, replace=False) for si in syst_indices]).astype(np.int32)
        np.random.shuffle(syst_indices)
        X_train = X_train[syst_indices.tolist()]
        Y_train = Y_train[syst_indices.tolist()]
        print 'Done\n'

    idx2sys = {idx: syst for idx, syst in enumerate(mt_systems)}

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
        folder_out = data_type + '_b%d' % balance
        path_out = path_data + 'params/' + mode + '/' + clf_name + '_' + folder_out + '/'
        if not os.path.exists(path_out):
            os.makedirs(path_out)

        print 'Saving predictions ...'
        cPickle.dump(pred_dev, open(path_out + folder_out + '_pred_dev.pkl', 'w'))
        cPickle.dump(pred_test, open(path_out + folder_out + '_pred_test.pkl', 'w'))
        print 'Done\n'

        print 'Saving model ...'
        joblib.dump(model, path_out + folder_out + '_model.pkl')
        print 'Done\n'


if __name__ == '__main__':
    clf()
