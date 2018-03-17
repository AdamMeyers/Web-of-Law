# -*- coding: utf-8 -*-

import sys
import time
import string
import cPickle
import xlsxwriter
import multiprocessing
import numpy as np
from collections import Counter


def print_proc_bar(curr_index, total, proc_bar_width=40):
    proc = float(curr_index) / total
    proc_count = int(proc * proc_bar_width)
    print '\r[%s] %.2f%%' % ('=' * proc_count + ' ' * (proc_bar_width - proc_count), proc * 100),


def format_prob(path_data='../data/europarl/',
                path_prob='params/prob_euro0.pkl',
                data_text='europarl-v7.es-en.en.tok.lower.numbered.10000'):
    """
    Take the probability outputted by the model, and the text file for which the predictions are made,
    go through the text file and replace each token by its probability of not being translated.
    Output filename is <data_text> followed by a ".prob" suffix.
    :param path_data: Path to the directory where the following files are located
    :param path_prob: Path to the probabilities outputted by the model
    :param data_text: Name of the text file for which the predictions are made
    """
    prob = cPickle.load(open(path_data + path_prob, 'r'))
    max_len = prob.shape[1]
    curr_line_num = None
    sent_prob_buffer = list()
    print 'Processing ...'
    with open(path_data + data_text + '.prob', 'w') as fout:
        with open(path_data + data_text + '.' + str(max_len), 'r') as fin:
            total_line = sum(1 for _ in fin)
            fin.seek(0)
            for curr_idx, line in enumerate(fin):
                line_num, sent, _ = line.rstrip('\r\n').split('\t')
                sent = sent.split(' ')
                line_prob = ['{:.4f}'.format(p) for p in prob[curr_idx]]

                if curr_line_num is None:
                    curr_line_num = line_num

                if curr_line_num != line_num:
                    fout.write(curr_line_num + '\t' + ' '.join(sent_prob_buffer) + '\n')
                    curr_line_num = line_num
                    sent_prob_buffer = list()

                try:
                    line_prob = line_prob[:sent.index('#####')]
                except ValueError:
                    pass

                sent_prob_buffer += line_prob

                print_proc_bar(curr_idx + 1, total_line)

        fout.write(curr_line_num + '\t' + ' '.join(sent_prob_buffer) + '\n')
    print '\nDone\n'


def get_confusion_matrix(path_data='../data/europarl/',
                         path_prob='params/termProb_euro0.pkl',
                         data_text='europarl-v7.es-en.en.tok.lower.numbered.10000'):
    """
    Take the probability outputted by the model, and the text file for which the predictions are made,
    for each token in the text file , compute the count of True Positives (TP), False Positives (FP),
    True Negatives (TN), False Negatives (FN), totcal occurrences, precision, recall, and F1 score;
    rank the tokens first by their F1 score, then by total occurrences, and lastly by alphabetical order;
    write the states to an xlsx file.
    Output filename is <data_text> followed by a ".cm.xlsx" suffix.
    :param path_data: Path to the directory where the following files are located
    :param path_prob: Path to the probabilities outputted by the model
    :param data_text: Name of the text file for which the predictions are made
    """
    print 'Loading data ...'
    word2idx = cPickle.load(open(path_data + 'word2idx.pkl', 'r'))
    idx2word = dict([(v, k) for k, v in word2idx.iteritems()])
    prob = cPickle.load(open(path_data + path_prob, 'r'))
    pred = prob > 0.5

    max_len = prob.shape[1]
    X, Y = cPickle.load(open(path_data + data_text + '.' + str(max_len) + '.dat', 'r'))
    print 'Done\n'

    print 'Creating counters ...'
    Y[np.nonzero(pred == 1)] -= 2
    tp = Counter([idx2word[idx] for idx in X[np.nonzero(Y == -1)] if idx2word[idx] != '#####'])
    fp = Counter([idx2word[idx] for idx in X[np.nonzero(Y == -2)] if idx2word[idx] != '#####'])
    tn = Counter([idx2word[idx] for idx in X[np.nonzero(Y == 0)] if idx2word[idx] != '#####'])
    fn = Counter([idx2word[idx] for idx in X[np.nonzero(Y == 1)] if idx2word[idx] != '#####'])
    print 'Done\n'

    print 'Creating confusion matrix ...'
    vocab = set().union(tp.keys(), fp.keys(), tn.keys(), fn.keys())
    dtypes = [('Term', np.unicode_, 16),
              ('TP', np.int32), ('FP', np.int32), ('TN', np.int32), ('FN', np.int32), ('Total', np.int32),
              ('Precision', np.float32), ('Recall', np.float32), ('F1', np.float32)]
    conf_mat = np.array([(unicode(w, 'utf-8'), tp[w], fp[w], tn[w], fn[w], 0, 0., 0., 0.) for w in vocab], dtype=dtypes)
    conf_mat['Total'] = conf_mat['TP'] + conf_mat['FP'] + conf_mat['TN'] + conf_mat['FN']

    pred_pos = (conf_mat['TP'] + conf_mat['FP']).astype(np.float32)
    pred_pos[np.nonzero(pred_pos == 0)] = 1
    conf_mat['Precision'] = conf_mat['TP'] / pred_pos

    real_pos = (conf_mat['TP'] + conf_mat['FN']).astype(np.float32)
    real_pos[np.nonzero(real_pos == 0)] = 1
    conf_mat['Recall'] = conf_mat['TP'] / real_pos

    denom = conf_mat['Precision'] + conf_mat['Recall']
    denom[np.nonzero(denom == 0.)] = 1.
    conf_mat['F1'] = 2 * conf_mat['Precision'] * conf_mat['Recall'] / denom

    conf_mat[::-1].sort(order=['F1', 'Total', 'Term'])

    all_tp, all_fp, all_tn, all_fn = sum(tp.values()), sum(fp.values()), sum(tn.values()), sum(fn.values())
    all_total = all_tp + all_fp + all_tn + all_fn
    all_prec = float(all_tp) / (all_tp + all_fp)
    all_rec = float(all_tp) / (all_tp + all_fn)
    all_f1 = 2 * all_prec * all_rec / (all_prec + all_rec)
    all_row = np.array([(u'Overall', all_tp, all_fp, all_tn, all_fn, all_total,
                         all_prec, all_rec, all_f1)], dtype=dtypes)

    conf_mat = np.concatenate([all_row, conf_mat])
    print 'Done\n'

    print 'Writing out ...'
    suffix = '.cm.xlsx'
    if 'termProb' in path_prob:
        suffix = '.term' + suffix
    workbook = xlsxwriter.Workbook(path_data + data_text + suffix)
    worksheet = workbook.add_worksheet()

    header = [dt[0] for dt in dtypes]
    columns = [c + '2' for c in list(string.ascii_uppercase)[:len(header)]]
    worksheet.write_row('A1', header)
    for h, c in zip(header, columns):
        worksheet.write_column(c, conf_mat[h])
    workbook.close()
    print 'Done\n'


def lt_crawl(inp):
    """
    Target function for multiprocessing.
    """
    term_len = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 23, 24, 26]

    proc_id, terms, lines = inp
    prog_count = 0
    prog_interval = 5
    start = time.time()
    labels = dict()
    for curr_idx, line in enumerate(lines):
        line_num, sent = line.rstrip('\r\n').split('\t')
        line_num = int(line_num)
        sent = sent.split(' ')
        labels[line_num] = np.array(['0'] * len(sent))

        for l in term_len:
            for i in range(len(sent[:-l])):
                if ' '.join(sent[i: i+l]) in terms:
                    labels[line_num][i: i+l] = '1'

        labels[line_num] = ' '.join(labels[line_num])

        if (curr_idx + 1) * 100. / len(lines) > prog_count * prog_interval:
            print 'Pid %d: completed %d%% in %.2f seconds' % (
                proc_id, prog_count * prog_interval, time.time() - start)
            prog_count += 1
            start = time.time()
            sys.stdout.flush()

    return proc_id, labels


def label_term(path_data='../data/',
               data_text='europarl/europarl-v7.es-en.en.tok.lower.numbered.10000',
               data_term='termolator_terms.uniq.tok.lower.pkl',
               n_proc=1):
    """
    Take the text file which contains the tokens and the list of terms identified by Termolator,
    go through the file and replace each token by 1 or 0 based on whether it belongs to a term
    identified by Termolator.
    Output filename is <data_text> followed by a ".term" suffix.
    :param path_data: Path to the directory where the following files are located
    :param data_text: Name of the text file to be labeled
    :param data_term: Path to the set of terms identified by Termolator
    :param n_proc: Number of subprocesses that will be spawned
    """
    print 'Loading data ...'
    terms = cPickle.load(open(path_data + data_term, 'r'))
    lines = [line for line in open(path_data + data_text, 'r')]
    print 'Done\n'

    batch_size = len(lines) / n_proc + 1
    inputs = [(proc_id, terms, lines[proc_id * batch_size: (proc_id + 1) * batch_size]) for proc_id in range(n_proc)]
    results = dict()
    pool = multiprocessing.Pool(n_proc)
    for r in pool.imap(lt_crawl, inputs):
        results[r[0]] = r[1]
    pool.close()
    pool.join()

    print 'Writing out ...'
    with open(path_data + data_text + '.term', 'w') as fout:
        for i in range(n_proc):
            for line_num in sorted(results[i].keys()):
                fout.write(str(line_num) + '\t' + results[i][line_num] + '\n')
    print 'Done\n'


def add_term_prob(path_data='../data/',
                  data_text='europarl/europarl-v7.es-en.en.tok.lower.numbered.10000',
                  extra_prob=.2,
                  max_len=50,
                  path_new_prob='europarl/params/termProb_euro2.pkl'):
    """
    Suppose <data_text> + ".prob" and <data_text> + ".term" have been produced.
    Add some extra probabilities to those in <data_text> + ".prob" where
    the corresponding location in <data_text> + ".term" has an 1.
    Output filename is <data_text> followed by a ".term.prob" suffix.
    Also create a matrix of the new probabilities in the same format as outputted by the model,
    which could then be used in get_confusion_matrix()
    :param path_data: Path to the directory where the relevant files are located
    :param data_text: Name of the text file for which ".prob" and ".term" files have been produced
    :param extra_prob: Extra probabilities to be added
    :param max_len: The length of each row in the new matrix of probabilities
    :param path_new_prob: Path where the new matrix will be saved
    """
    termProb = list()
    with open(path_data + data_text + '.term.prob', 'w') as fout:
        with open(path_data + data_text + '.prob', 'r') as f_prob:
            total_line = sum(1 for _ in f_prob)
            f_prob.seek(0)
            with open(path_data + data_text + '.term', 'r') as f_term:
                for idx, lines in enumerate(zip(f_prob, f_term)):
                    line_num, probs = lines[0].rstrip('\r\n').split('\t')
                    probs = np.array([float(p) for p in probs.split(' ')])
                    terms = np.array([t for t in lines[1].rstrip('\r\n').split('\t')[1].split(' ')])
                    probs[np.nonzero(terms == '1')] += extra_prob
                    probs = np.minimum(probs, 1.)
                    out_probs = ' '.join(['{:.4f}'.format(p) for p in probs])
                    fout.write(line_num + '\t' + out_probs + '\n')

                    while len(probs) > max_len:
                        termProb += [probs[:max_len]]
                        probs = probs[max_len:]
                    if len(probs) < max_len:
                        probs = np.concatenate([probs, np.zeros((max_len - len(probs)), dtype=np.float32)])
                    termProb += [probs]

                    print_proc_bar(idx + 1, total_line)
    termProb = np.stack(termProb)
    print '\ntermProb shape', termProb.shape
    cPickle.dump(termProb, open(path_data + path_new_prob, 'w'))


if __name__ == '__main__':
    format_prob()
    get_confusion_matrix()
    label_term()
    add_term_prob()
