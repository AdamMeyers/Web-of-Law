from utils import *


class Model4(nn.Module):
    def __init__(self, params, embeddings):
        super(Model4, self).__init__()
        self.l_emb_src = embeddings['src']
        self.l_emb_tgt = embeddings['tgt']
        self.l_birnn_src = GRUBiRNNWord(params['dim_emb'], params['dim_hid'], params['num_rnn_layer'])
        self.l_birnn_tgt = GRUBiRNNWord(params['dim_emb'], params['dim_hid'], params['num_rnn_layer'])
        self.l_relational = RelationalNet(params['dim_hid'], params['dropout'])
        self.l_out = nn.Sequential(
            torch.nn.Linear(params['dim_hid'], params['n_classes']),
            torch.nn.LogSoftmax(1)
        )

    def forward(self, x):
        x_src, seq_lens_src = self.l_emb_src(x['src'])
        x_src = self.l_birnn_src(x_src, seq_lens_src)
        z = []
        for x_tgt in x['tgt']:
            x_tgt, seq_lens_tgt = self.l_emb_tgt(x_tgt)
            x_tgt = self.l_birnn_tgt(x_tgt, seq_lens_tgt)
            z += [self.l_relational(x_src, seq_lens_src, x_tgt, seq_lens_tgt)]
        z = torch.stack(z).mean(0)
        z = self.l_out(z)
        return z
