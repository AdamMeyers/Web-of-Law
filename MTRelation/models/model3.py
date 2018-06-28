from utils import *


class Model3(nn.Module):
    def __init__(self, params, embeddings):
        super(Model3, self).__init__()
        self.l_emb_src = embeddings['src']
        self.l_emb_tgt = embeddings['tgt']
        self.l_birnn_src = GRUBiRNN(params['dim_emb'], params['dim_hid'], params['num_rnn_layer'])
        self.l_birnn_tgt = GRUBiRNN(params['dim_emb'], params['dim_hid'], params['num_rnn_layer'])
        self.l_ff = nn.Sequential(
            torch.nn.Linear(4 * params['dim_hid'], params['dim_hid']),
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
        x = torch.stack([torch.cat([x_src, x_tgt_i], dim=1) for x_tgt_i in x_tgt])
        x = self.l_ff(x).mean(0)
        x = self.l_out(x)
        return x
