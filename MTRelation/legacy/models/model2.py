from utils import *


class Model2(nn.Module):
    def __init__(self, params):     # , embeddings
        super(Model2, self).__init__()
        # embedding_src = embeddings['src']
        # embedding_tgt = embeddings['tgt']
        embedding_src = load_emb(params['path_data'], suffix='en')
        embedding_tgt = load_emb(params['path_data'], suffix='es')

        self.l_birnn_src = GRUBiRNN(embedding_src, params['dim_hid'], params['num_rnn_layer'])
        self.l_birnn_tgt = GRUBiRNN(embedding_tgt, params['dim_hid'], params['num_rnn_layer'])
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
        x_src = self.l_birnn_src(x['src'])
        x_tgt = torch.stack([self.l_birnn_tgt(x_tgt) for x_tgt in x['tgt']]).mean(0)
        x = torch.cat([x_src, x_tgt], dim=1)
        x = self.l_ff(x)
        x = self.l_out(x)
        return x
