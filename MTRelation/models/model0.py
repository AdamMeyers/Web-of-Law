from utils import *


class Model0(nn.Module):
    def __init__(self, params, embeddings):
        super(Model0, self).__init__()
        self.l_emb = embeddings['src']
        self.l_birnn = GRUBiRNNWord(params['dim_emb'], params['dim_hid'], params['num_rnn_layer'])
        self.l_relational = RelationalNet(params['dim_hid'], params['dropout'])
        self.l_out = nn.Sequential(
            torch.nn.Linear(params['dim_hid'], params['n_classes']),
            torch.nn.LogSoftmax(1)
        )

    def forward(self, x):
        x, seq_lens = self.l_emb(x['src'])
        x = self.l_birnn(x, seq_lens)
        x = self.l_relational(x, seq_lens, x, seq_lens)
        x = self.l_out(x)
        return x
