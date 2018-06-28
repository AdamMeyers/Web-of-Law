from utils import *


class ModelBiRNN(nn.Module):
    def __init__(self, params):     # , embeddings
        super(ModelBiRNN, self).__init__()
        # embedding_src = embeddings['src']
        embedding_src = load_emb(params['path_data'], suffix='en')
        # self.l_birnn = GRUBiRNN(embedding_src, params['dim_hid'], params['num_rnn_layer'])
        self.l_birnn = LSTMBiRNN(embedding_src, params['dim_hid'], params['num_rnn_layer'])
        self.l_ff = nn.Sequential(
            torch.nn.Linear(2 * params['dim_hid'], params['dim_hid']),
            torch.nn.Dropout(params['dropout']),
            torch.nn.ReLU()
        )
        self.l_out = nn.Sequential(
            torch.nn.Linear(params['dim_hid'], params['n_classes']),
            torch.nn.LogSoftmax(1)
        )

    def forward(self, x):
        x = self.l_birnn(x['src'])
        x = self.l_ff(x)
        x = self.l_out(x)
        return x
