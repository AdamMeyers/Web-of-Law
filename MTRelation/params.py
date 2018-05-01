param_toy_rnn = {
    'sent_len': 4,
    'dim_emb': 3,
    'dim_hid': 2,
    'num_rnn_layer': 1,
    'dropout': 0.
}

param_toy_cnn = {
    'sent_len': 4,
    'dim_emb': 3,
    'dim_hid': 2,
    'kernel_num': 3,
    'kernel_sizes': [2, 3],
    'dropout': 0.
}

param_rnn = {
    'sent_len': 100,
    'dim_emb': 300,
    'dim_hid': 300,
    'num_rnn_layer': 1,
    'dropout': 0.5
}

param_cnn = {
    'sent_len': 100,
    'dim_emb': 300,
    'dim_hid': 300,
    'kernel_num': 300,
    'kernel_sizes': [2, 3, 4, 5],
    'dropout': 0.5
}
