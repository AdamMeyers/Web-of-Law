import cPickle
import numpy as np


def print_proc_bar(curr_index, total, proc_bar_width=40):
    proc = float(curr_index) / total
    proc_count = int(proc * proc_bar_width)
    print '\r[%s] %.2f%%' % ('=' * proc_count + ' ' * (proc_bar_width - proc_count), proc * 100),


def main(path_data='../data/',
         file_name='europarl-v7.es-en.en.tok.lower',
         max_len=50):
    print 'Loading word-to-index map ...'
    word2idx = cPickle.load(open(path_data + 'word2idx.pkl', 'r'))
    print 'Done', '\n'

    print 'Loading untranslated words ...'
    untrans = set()
    with open(path_data + 'europarl-v7.es-en.en.tok.non-translated', 'r') as fin:
        for line in fin:
            untrans.add(line.rstrip('\r\n').lower())
    print 'Done\n'

    print 'Processing data ...'
    data_X, data_target = list(), list()
    with open(path_data + file_name, 'r') as fin:
        total_line = sum(1 for _ in fin)
        fin.seek(0)
        for curr_idx, line in enumerate(fin):
            sent = line.rstrip('\r\n').lower().split()

            sent_proc, target = list(), list()
            for w in sent:
                if not w.isalpha():
                    sent_proc += [str(word2idx['#NOT_ALPHA#'])]
                elif w not in word2idx:
                    sent_proc += [str(word2idx['UNK'])]
                else:
                    sent_proc += [str(word2idx[w])]

                if w in untrans:
                    target += ['1']
                else:
                    target += ['0']

            while len(sent_proc) > max_len:
                data_X += [sent_proc[:max_len]]
                data_target += [target[:max_len]]
                sent_proc = sent_proc[max_len:]
                target = target[max_len:]

            sent_proc += [str(word2idx['#####'])] * (max_len - len(sent_proc))
            target += ['0'] * (max_len - len(target))
            data_X += [sent_proc]
            data_target += [target]

            print_proc_bar(curr_idx + 1, total_line)
    print '\nDone\n'

    data_X = np.array(data_X).astype('int32')
    data_target = np.array(data_target).astype('int32')

    print 'Dumping ...'
    cPickle.dump([data_X, data_target], open(path_data + file_name + '.dat', 'w'))
    print 'Done\n'


if __name__ == '__main__':
    main()
