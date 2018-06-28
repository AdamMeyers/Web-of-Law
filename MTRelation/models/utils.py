import torch
import torch.nn as nn
from torch.autograd import Variable
from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence
import cPickle
import numpy as np


def load_emb(path_data, suffix):
    with open(path_data + 'embedding_%s.pkl' % suffix, 'r') as fin:
        return cPickle.load(fin)


def create_var(data):
    var = Variable(data)
    if torch.cuda.is_available():
        var = var.cuda()
    return var


class Embedding(nn.Module):
    def __init__(self, path_data, suffix):
        super(Embedding, self).__init__()
        with open(path_data + 'word2idx_' + suffix + '.pkl', 'r') as f_w2i:
            self.word2idx = cPickle.load(f_w2i)
        with open(path_data + 'embedding_' + suffix + '.pkl', 'r') as f_emb:
            embedding = cPickle.load(f_emb)
        self.l_emb = nn.Embedding(embedding.shape[0], embedding.shape[1], sparse=True)
        self.l_emb.weight.data.copy_(torch.from_numpy(embedding))
        self.vocab_size = embedding.shape[0]

    def forward(self, x):
        x_proc = []
        max_len = 0
        for line in x:
            x_proc += [[self.word2idx[w] if w in self.word2idx else self.word2idx['UNK'] for w in line]]
            if len(line) > max_len:
                max_len = len(line)
        for line in x_proc:
            line += [self.word2idx['PADDING']] * (max_len - len(line))
        x_proc = np.array(x_proc).astype(np.int64)
        seq_lens = np.sum(x_proc != self.word2idx['PADDING'], axis=1)
        x_proc = create_var(torch.from_numpy(x_proc))
        return self.l_emb(x_proc), seq_lens


class GRUBiRNN(nn.Module):
    def __init__(self, dim_in, dim_hid, num_rnn_layer):
        super(GRUBiRNN, self).__init__()
        self.l_birnn = nn.GRU(dim_in, dim_hid, num_rnn_layer, bidirectional=True)

    def forward(self, x, seq_lens):
        perm_indices = np.argsort(-1 * seq_lens)
        x = x[perm_indices].transpose(0, 1)
        seq_lens = seq_lens[perm_indices]

        x = pack_padded_sequence(x, seq_lens)
        _, hn = self.l_birnn(x)
        x = torch.cat([hn[0], hn[1]], dim=1)

        perm_indices_rev = torch.from_numpy(np.argsort(perm_indices))
        if torch.cuda.is_available():
            perm_indices_rev = perm_indices_rev.cuda()
        return x[perm_indices_rev]


class LSTMBiRNN(nn.Module):
    def __init__(self, dim_in, dim_hid, num_rnn_layer):
        super(LSTMBiRNN, self).__init__()
        self.l_birnn = nn.LSTM(dim_in, dim_hid, num_rnn_layer, bidirectional=True)

    def forward(self, x, seq_lens):
        perm_indices = np.argsort(-1 * seq_lens)
        x = x[perm_indices].transpose()
        seq_lens = seq_lens[perm_indices]

        x = pack_padded_sequence(x, seq_lens)
        _, hn = self.l_birnn(x)
        x = torch.cat([hn[0][0], hn[0][1]], dim=1)

        perm_indices_rev = torch.from_numpy(np.argsort(perm_indices))
        if torch.cuda.is_available():
            perm_indices_rev = perm_indices_rev.cuda()
        return x[perm_indices_rev]


class GRUBiRNNWord(nn.Module):
    def __init__(self, dim_in, dim_hid, num_rnn_layer):
        super(GRUBiRNNWord, self).__init__()
        self.l_birnn = nn.GRU(dim_in, dim_hid, num_rnn_layer, batch_first=True, bidirectional=True)

    def forward(self, x, seq_lens):
        perm_indices = np.argsort(-1 * seq_lens)
        x = x[perm_indices]
        seq_lens = seq_lens[perm_indices]

        x = pack_padded_sequence(x, seq_lens, batch_first=True)
        x, _ = self.l_birnn(x)
        x, _ = pad_packed_sequence(x, batch_first=True)

        perm_indices_rev = torch.from_numpy(np.argsort(perm_indices))
        if torch.cuda.is_available():
            perm_indices_rev = perm_indices_rev.cuda()
        return x[perm_indices_rev]


class RelationalNet(nn.Module):
    def __init__(self, dim_hid, dropout):
        super(RelationalNet, self).__init__()
        self.l_ff = nn.Sequential(
            torch.nn.Linear(4 * dim_hid, dim_hid),
            torch.nn.Dropout(dropout),
            torch.nn.ReLU()
        )

    def forward(self, x1, seq_lens1, x2, seq_lens2):
        x_pair_all = []
        max_len = np.max(seq_lens1) * np.max(seq_lens2)
        for x_seq1, sl1, x_seq2, sl2 in zip(x1, seq_lens1, x2, seq_lens2):
            i1 = torch.from_numpy(
                np.concatenate([[i] * sl2 for i in range(sl1)]).astype(np.int64)
            )
            i2 = torch.from_numpy(
                np.array([i for i in range(sl2)] * sl1, dtype=np.int64)
            )
            if torch.cuda.is_available():
                i1, i2 = i1.cuda(), i2.cuda()
            x_pair = torch.cat([x_seq1[i1], x_seq2[i2]], dim=1)
            if max_len > sl1 * sl2:
                padding = Variable(torch.zeros((max_len - sl1 * sl2, x_pair.size()[1]))).float()
                if torch.cuda.is_available():
                    padding = padding.cuda()
                x_pair = torch.cat([x_pair, padding])
            x_pair_all += [x_pair]
        x_pair_all = torch.stack(x_pair_all)
        denom = Variable(torch.from_numpy(seq_lens1 * seq_lens2)[:, np.newaxis]).float()
        if torch.cuda.is_available():
            denom = denom.cuda()
        return self.l_ff(x_pair_all).sum(1) / denom
