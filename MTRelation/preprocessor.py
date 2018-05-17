import cPickle
import numpy as np


def print_proc_bar(curr_index, total, proc_bar_width=40):
    proc = float(curr_index) / total
    proc_count = int(proc * proc_bar_width)
    print '\r[%s] %.2f%%' % ('=' * proc_count + ' ' * (proc_bar_width - proc_count), proc * 100),


def get_data_size(total, data_split):
    train_size = int(total * data_split[0])
    test_size = int(total * data_split[1])
    dev_size = total - train_size - test_size
    return train_size, dev_size, test_size


def create_y(path_data, path_scores, mt_systems, data_split):
    print 'Creating Y ...'
    y = np.argmax(
        np.array(
            [cPickle.load(open(path_scores + syst + '.pkl', 'r')) for syst in mt_systems]
        ),
        axis=0
    ).astype(np.int32)
    train_size, _, test_size = get_data_size(y.shape[0], data_split)
    for dat, dat_name in zip([y[:train_size], y[train_size: -test_size], y[-test_size:]],
                             ['Y_train', 'Y_dev', 'Y_test']):
        print dat_name, ':', dat.shape
        cPickle.dump(dat, open(path_data + dat_name + '.pkl', 'w'))
    print 'Done\n'


def create_x(path_data, path_corpus, max_len, data_split, word2idx, suffix):
    print 'Creating X for %s ...' % suffix
    x = []
    with open(path_corpus, 'r') as fin:
        total_lines = sum([1 for _ in fin])
        fin.seek(0)
        for curr_idx, line in enumerate(fin):
            line_proc = np.array([word2idx[w] if w in word2idx else word2idx['UNK'] for w in line.rstrip('\r\n').split(' ')])
            if len(line_proc) > max_len:
                keep_idx = np.sort(np.random.choice(np.arange(len(line_proc)), size=max_len, replace=False))
                line_proc = line_proc[keep_idx]
            if len(line_proc) < max_len:
                line_proc = np.concatenate([line_proc, np.array([word2idx['PADDING']] * (max_len - len(line_proc)))])
            x += [line_proc]
            print_proc_bar(curr_idx + 1, total_lines)
    print
    x = np.stack(x).astype(np.int32)
    train_size, _, test_size = get_data_size(x.shape[0], data_split)
    for dat, dat_name in zip([x[:train_size], x[train_size: -test_size], x[-test_size:]],
                             ['X_train_', 'X_dev_', 'X_test_']):
        dat_name += suffix
        print dat_name, ':', dat.shape
        cPickle.dump(dat, open(path_data + dat_name + '.pkl', 'w'))
    print 'Done\n'


def main(path_data='../data/',
         path_corpus='/scratch/wl1191/MTScore/data/',
         file_src='en.2016.omega.tm',
         file_tgt='es.2016.omega.tm',
         mt_systems=('moses', 'apertium', 'nematus'),
         max_len=100,
         data_split=(0.8, 0.1, 0.1)):
    print 'Loading word-to-index map ...'
    word2idx_en = cPickle.load(open(path_data + 'word2idx_en.pkl', 'r'))
    word2idx_es = cPickle.load(open(path_data + 'word2idx_es.pkl', 'r'))
    print 'Done\n'

    create_y(path_data, path_corpus + file_tgt + '.score.', mt_systems, data_split)
    create_x(path_data, path_corpus + file_src, max_len, data_split, word2idx_en, 'en')
    for syst in mt_systems:
        create_x(path_data, path_corpus + file_tgt + '.' + syst, max_len, data_split, word2idx_es, syst)


if __name__ == '__main__':
    main()
