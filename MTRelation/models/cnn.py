import torch.nn.functional as F
from utils import *


class ModelCNN(nn.Module):
    def __init__(self, params):     # , embeddings
        super(ModelCNN, self).__init__()
        # embedding_src = embeddings['src']
        embedding_src = load_emb(params['path_data'], suffix='en')
        self.l_emb = nn.Embedding(embedding_src.shape[0], params['dim_emb'])
        self.l_emb.weight.data.copy_(torch.from_numpy(embedding_src))

        self.convs = nn.ModuleList([
            nn.Conv2d(1, params['kernel_num'], (ks, params['dim_emb'])) for ks in params['kernel_sizes']
        ])
        self.dropout = nn.Dropout(params['dropout'])
        self.l_ff = nn.Sequential(
            torch.nn.Linear(params['kernel_num'] * len(params['kernel_sizes']), params['dim_hid']),
            torch.nn.Dropout(params['dropout']),
            torch.nn.ReLU()
        )
        self.l_out = nn.Sequential(
            torch.nn.Linear(params['dim_hid'], params['n_classes']),
            torch.nn.LogSoftmax(1)
        )

    def forward(self, x):
        x = create_var(torch.from_numpy(x['src']))
        x = self.l_emb(x)
        x = x.unsqueeze(1)
        x = [F.relu(cv(x)).squeeze(3) for cv in self.convs]
        x = [F.max_pool1d(i, i.size(2)).squeeze(2) for i in x]
        x = self.dropout(torch.cat(x, 1))
        x = self.l_ff(x)
        x = self.l_out(x)
        return x
