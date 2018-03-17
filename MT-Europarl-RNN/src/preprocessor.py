import cPickle
import numpy as np


def print_proc_bar(curr_index, total, proc_bar_width=40):
    proc = float(curr_index) / total
    proc_count = int(proc * proc_bar_width)
    print '\r[%s] %.2f%%' % ('=' * proc_count + ' ' * (proc_bar_width - proc_count), proc * 100),


def main(path_data='../data/europarl/',
         file_text='europarl-v7.es-en.en.tok.lower.numbered',   # 'en.2016.omega.tm.tok.lower.numbered'
         file_label='europarl-v7.es-en.en.tok.labels',    # 'en.2016.omega.tm.tok.labels.untrans'
         max_len=50):
    print 'Loading word-to-index map ...'
    word2idx = cPickle.load(open(path_data + 'word2idx.pkl', 'r'))
    print 'Done\n'

    # for suffix in ['.train', '.dev', '.test']:
    for suffix in ['.10000.dgt', '.10000']:     # '.moses.all'
        print 'Processing %s data ...' % suffix[1:]
        data_X, data_Y = list(), list()
        with open(path_data + file_text + suffix + '.' + str(max_len), 'w') as fout:
            with open(path_data + file_text + suffix, 'r') as f_text:
                with open(path_data + file_label + suffix, 'r') as f_label:
                    total_line = sum(1 for _ in f_text)
                    f_text.seek(0)
                    for curr_idx, lines in enumerate(zip(f_text, f_label)):
                        line_text, line_label = lines
                        line_num, sent = line_text.rstrip('\r\n').split('\t')
                        sent = sent.split(' ')

                        sent_proc = list()
                        for w in sent:
                            if w in word2idx:
                                sent_proc += [word2idx[w]]
                            elif not w.isalpha():
                                sent_proc += [word2idx['#NOT_ALPHA#']]
                            else:
                                sent_proc += [word2idx['UNK']]
                        target = line_label.rstrip('\r\n').split(' ')

                        while len(sent_proc) > max_len:
                            fout.write(
                                line_num + '\t' + ' '.join(sent[:max_len]) + '\t' + ' '.join(target[:max_len]) + '\n'
                            )
                            sent = sent[max_len:]

                            data_X += [sent_proc[:max_len]]
                            data_Y += [[int(l) for l in target[:max_len]]]
                            sent_proc = sent_proc[max_len:]
                            target = target[max_len:]

                        sent += ['#####'] * (max_len - len(sent))
                        sent_proc += [word2idx['#####']] * (max_len - len(sent_proc))
                        target += ['0'] * (max_len - len(target))

                        fout.write(line_num + '\t' + ' '.join(sent) + '\t' + ' '.join(target) + '\n')

                        data_X += [sent_proc]
                        data_Y += [[int(l) for l in target]]

                        print_proc_bar(curr_idx + 1, total_line)
        print '\nDone\n'

        data_X = np.array(data_X).astype('int32')
        data_Y = np.array(data_Y).astype('int32')

        print 'Dumping ...'
        cPickle.dump([data_X, data_Y], open(path_data + file_text + suffix + '.' + str(max_len) + '.dat', 'w'))
        print 'Done\n'

        print 'Shape of X:', data_X.shape, '\n'
        print 'Shape of Y:', data_Y.shape, '\n'


if __name__ == '__main__':
    main()
