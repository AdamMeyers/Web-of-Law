from utils import *


class Model4(nn.Module):
    def __init__(self, params):     # , embeddings
        super(Model4, self).__init__()
        # embedding_src = embeddings['src']
        # embedding_tgt = embeddings['tgt']
        embedding_src = load_emb(params['path_data'], suffix='en')
        embedding_tgt = load_emb(params['path_data'], suffix='es')

        self.l_birnn_src = GRUBiRNNWord(embedding_src, params['dim_hid'], params['num_rnn_layer'])
        self.l_birnn_tgt = GRUBiRNNWord(embedding_tgt, params['dim_hid'], params['num_rnn_layer'])
        self.l_relational = RelationalNet(params['dim_hid'], params['dropout'])
        self.l_out = nn.Sequential(
            torch.nn.Linear(params['dim_hid'], params['n_classes']),
            torch.nn.LogSoftmax(1)
        )

    def forward(self, x):
        x_src, seq_lens_src = self.l_birnn_src(x['src'])
        z = []
        for x_tgt in x['tgt']:
            x_tgt, seq_lens_tgt = self.l_birnn_tgt(x_tgt)
            z += [self.l_relational(x_src, seq_lens_src, x_tgt, seq_lens_tgt)]
        z = torch.stack(z).mean(0)
        z = self.l_out(z)
        return z
