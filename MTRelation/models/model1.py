from utils import *


class Model1(nn.Module):
    def __init__(self, params, embeddings):
        super(Model1, self).__init__()
        self.l_emb_src = embeddings['src']
        self.l_emb_tgt = embeddings['tgt']
        self.l_birnn_src = GRUBiRNN(params['dim_emb'], params['dim_hid'], params['num_rnn_layer'])
        self.l_birnn_tgt = GRUBiRNN(params['dim_emb'], params['dim_hid'], params['num_rnn_layer'])
        self.l_ff = nn.Sequential(
            torch.nn.Linear(2 * (1 + params['n_classes']) * params['dim_hid'], params['dim_hid']),
            torch.nn.Dropout(params['dropout']),
            torch.nn.ReLU()
        )
        self.l_out = nn.Sequential(
            torch.nn.Linear(params['dim_hid'], params['n_classes']),
            torch.nn.LogSoftmax(1)
        )

    def forward(self, x):
        x_src = self.l_birnn_src(*self.l_emb_src(x['src']))
        x_tgt = [self.l_birnn_src(*self.l_emb_tgt(x_tgt)) for x_tgt in x['tgt']]
        x = torch.cat([x_src] + x_tgt, dim=1)
        x = self.l_ff(x)
        x = self.l_out(x)
        return x
