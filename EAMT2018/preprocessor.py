import cPickle
import numpy as np
from collections import OrderedDict


def print_proc_bar(curr_index, total, proc_bar_width=40):
    proc = float(curr_index) / total
    proc_count = int(proc * proc_bar_width)
    print '\r[%s] %.2f%%' % ('=' * proc_count + ' ' * (proc_bar_width - proc_count), proc * 100),


def main(path_data='../data/',
         corpus='en.2016.omega.tm.tok.lower',
         file_scores=OrderedDict([('moses', 'es.2016.omega.tm.score.moses.pkl'),
                                  ('apertium', 'es.2016.omega.tm.score.apertium.pkl'),
                                  ('nematus', 'es.2016.omega.tm.score.nematus.pkl')]),
         max_len=100):
    print 'Loading word-to-index map ...'
    word2idx = cPickle.load(open(path_data + 'word2idx.pkl', 'r'))
    print 'Done\n'

    print 'Processing ...'
    Y = np.argmax(
        np.array(
            [cPickle.load(open(path_data + file_scores[syst], 'r')) for syst in file_scores]
        ),
        axis=0
    ).astype(np.int32)

    X = list()
    with open(path_data + corpus, 'r') as fin:
        for curr_idx, line in enumerate(fin):
            line_proc = np.array([word2idx[w] if w in word2idx else 0 for w in line.rstrip('\r\n').split(' ')])
            if len(line_proc) > max_len:
                keep_idx = np.sort(np.random.choice(np.arange(len(line_proc)), size=max_len, replace=False))
                line_proc = line_proc[keep_idx]
            if len(line_proc) < max_len:
                line_proc = np.concatenate([line_proc, np.array([-1] * (max_len - len(line_proc)))])
            X += [line_proc]
            print_proc_bar(curr_idx + 1, Y.shape[0])
    X = np.stack(X).astype(np.int32)
    print '\nDone\n'

    print 'Writing out ...'
    train_size = int(X.shape[0] * 0.8)
    eval_size = int(X.shape[0] * 0.1)

    X_train, Y_train = X[:train_size], Y[:train_size]
    X_dev, Y_dev = X[train_size: -eval_size], Y[train_size: -eval_size]
    X_test, Y_test = X[-eval_size:], Y[-eval_size:]

    print 'Train data size:', X_train.shape, Y_train.shape
    print 'Dev data size:', X_dev.shape, Y_dev.shape
    print 'Test data size:', X_test.shape, Y_test.shape

    for dat, dat_name in zip([X_train, Y_train, X_dev, Y_dev, X_test, Y_test],
                             ['X_train', 'Y_train', 'X_dev', 'Y_dev', 'X_test', 'Y_test']):
        cPickle.dump(dat, open(path_data + dat_name + '.pkl', 'w'))
    print 'Done\n'


if __name__ == '__main__':
    main()
