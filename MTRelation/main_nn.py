import os
import sys
import torch
import cPickle
import numpy as np
import pandas as pd
from params import *
from models.header import *
from models.utils import Embedding
from doc_iterator import DocIterator


np.random.seed(42)
torch.manual_seed(42)
torch.cuda.manual_seed_all(42)


def print_proc_bar(curr_index, total, proc_bar_width=40):
    proc = float(curr_index) / total
    proc_count = int(proc * proc_bar_width)
    print '\r[%s] %.2f%%' % ('=' * proc_count + ' ' * (proc_bar_width - proc_count), proc * 100),


def prepare_embeddings(model_id, params):
    embeddings = {'src': Embedding(params['path_data'], 'en')}
    if model_id[-1] in '1234':
        embeddings['tgt'] = Embedding(params['path_data'], 'es')
    return embeddings


def prepare_data(mode, params, mt_systems, load_tgt):
    x = {
        dat: {'src': DocIterator(params['path_doc'] + 'en.2016.omega.tm.tok.lower.' + dat)}
        for dat in ['train', 'dev', 'test']
    }
    if load_tgt:
        for dat in x:
            x[dat]['tgt'] = [
                DocIterator(params['path_doc'] + 'es.2016.omega.tm.' + syst + '.' + dat)
                for syst in mt_systems
            ]

    y = {
        dat: cPickle.load(open(params['path_data'] + mode + '/Y_' + dat + '.pkl', 'r')).astype(np.int64)
        for dat in ['train', 'dev', 'test']
    }
    return x, y


def get_x_batch(x, batch_size, batch_idx):
    x_batch = {'src': x['src'][batch_size * batch_idx: batch_size * (batch_idx + 1)]}
    if 'tgt' in x:
        x_batch['tgt'] = [x_tgt[batch_size * batch_idx: batch_size * (batch_idx + 1)] for x_tgt in x['tgt']]
    return x_batch


def train(M, optimizer, x, y, batch_size):
    num_batch = len(x['src']) / batch_size
    if len(x['src']) % batch_size > 0:
        num_batch += 1
    batch_indices = np.arange(num_batch)
    np.random.shuffle(batch_indices)
    total_loss = 0.
    for curr_idx, batch_idx in enumerate(batch_indices):
        x_batch = get_x_batch(x, batch_size, batch_idx)
        y_batch = y[batch_size * batch_idx: batch_size * (batch_idx + 1)]
        logprob = M(x_batch)
        loss = -1 * logprob[np.arange(y_batch.shape[0]), y_batch].mean()
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        total_loss += loss.data[0]
        if (curr_idx + 1) % 100 == 0:
            print 'Batch %d: %.5f' % (curr_idx + 1, loss.data[0])
            sys.stdout.flush()
        # print_proc_bar(curr_idx + 1, num_batch)
    # print
    return total_loss


def predict(M, x, batch_size):
    logprob = list()
    num_batch = len(x['src']) / batch_size
    if len(x['src']) % batch_size > 0:
        num_batch += 1
    for batch_idx in range(num_batch):
        x_batch = get_x_batch(x, batch_size, batch_idx)
        logprob += [np.array(M(x_batch).data)]
        if (batch_idx + 1) % 100 == 0:
            print 'Batch %d' % (batch_idx + 1)
            sys.stdout.flush()
        # print_proc_bar(batch_idx + 1, num_batch)
    # print
    return np.concatenate(logprob)


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
    print '\n', eval_table
    return accuracy


def main(
    path_data='/misc/proteus1/data/jortega/Web-of-Law/MT/MTRelation/data/',
    path_doc='/misc/proteus1/data/jortega/Web-of-Law/MT/MTRelation/doc/',
    mode='top3',    # 'prev', 'all', 'top3', or 'each3'
    model_id='3',   # 'BiRNN', '0', '1', '2', '3', or '4'
    batch_size=50,
    lr=0.025,
    nepoch=1,
    save_model=True,
    load_model=None,
):
    if mode == 'prev':
        mt_systems = ['moses', 'apertium', 'nematus']
    elif mode == 'all':
        mt_systems = ['moses', 'apertium', 'nematus', 'opennmt', 'cdec']
    elif mode == 'top3':
        mt_systems = ['nematus', 'opennmt', 'cdec']
    else:
        mt_systems = ['nematus', 'cdec', 'apertium']

    path_out = path_data + 'params/' + mode + '/model_%s/' % model_id
    if not os.path.exists(path_out):
        os.makedirs(path_out)

    idx2sys = {idx: syst for idx, syst in enumerate(mt_systems)}
    params = param_cnn if model_id == 'CNN' else param_rnn
    params['path_data'] = path_data
    params['path_doc'] = path_doc
    params['n_classes'] = len(idx2sys)

    print 'Loading word embeddings ...'
    embeddings = prepare_embeddings(model_id, params)
    print 'Done\n'

    print 'Initializing model ...'
    M = eval('Model' + model_id)(params, embeddings)
    if torch.cuda.is_available():
        M.cuda()
    if load_model is not None:
        print 'Loading model from %s ...' % load_model
        M.load_state_dict(torch.load(load_model))
    optimizer = torch.optim.Adagrad(M.parameters(), lr=lr)
    print 'Done\n'

    print 'Preparing data ...'
    x, y = prepare_data(mode, params, mt_systems, model_id[-1] in '1234')
    print 'Done\n'

    best_accuracy = 0.
    best_epoch = 0
    # for e in range(nepoch):
    e = -1
    while True:
        e += 1
        M.train(True)
        print '\nEpoch %d ...\n' % e
        total_loss = train(M, optimizer, x['train'], y['train'], batch_size)
        print 'Epoch %d Total loss: %.5f\n' % (e, total_loss)

        M.eval()
        print 'Epoch %d: Evaluating on dev ...' % e
        logprob_dev = predict(M, x['dev'], batch_size)
        accuracy = evaluate(np.argmax(logprob_dev, axis=1), y['dev'], idx2sys)
        print 'Done\n'

        print 'Epoch %d: Evaluating on test ...' % e
        logprob_test = predict(M, x['test'], batch_size)
        evaluate(np.argmax(logprob_test, axis=1), y['test'], idx2sys)
        print 'Done\n'

        if accuracy > best_accuracy:
            best_accuracy = accuracy
            best_epoch = e
            print 'New best epoch: %d\n' % e

            if save_model and e > 0:
                print 'Saving predictions ...'
                cPickle.dump(logprob_dev, open(path_out + 'prob_dev_' + str(e) + '.pkl', 'w'))
                cPickle.dump(logprob_test, open(path_out + 'prob_test_' + str(e) + '.pkl', 'w'))
                print 'Done\n'

                print 'Saving model to', path_out + 'epoch' + str(e) + '.pt', '\n'
                torch.save(M.state_dict(), path_out + 'epoch' + str(e) + '.pt')
                print 'Done\n'

        if e - best_epoch > 10:
            print 'Training completed. Best epoch: %d' % best_epoch
            break


if __name__ == '__main__':
    main()
