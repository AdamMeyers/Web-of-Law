import theano
import theano.tensor as T
import lasagne
import cPickle


class BiRNN:
    def __init__(self, params, emb_w):
        X = T.imatrix('input')
        mask = T.imatrix('mask')
        Y = T.ivector('label')

        l_X = lasagne.layers.InputLayer(shape=(params['batch_size'], params['max_len']), input_var=X)
        l_mask = lasagne.layers.InputLayer(shape=(params['batch_size'], params['max_len']), input_var=mask)
        l1 = lasagne.layers.EmbeddingLayer(
            l_X, input_size=params['vocab_size'], output_size=params['dim_emb'], W=emb_w
        )
        l_forward = lasagne.layers.GRULayer(
            l1, params['dim_hidden'], mask_input=l_mask, only_return_final=True
        )
        l_backward = lasagne.layers.GRULayer(
            l1, params['dim_hidden'], mask_input=l_mask, backwards=True, only_return_final=True
        )
        l_concat = lasagne.layers.ConcatLayer([l_forward, l_backward], axis=1)

        l_ff = lasagne.layers.DenseLayer(
            lasagne.layers.dropout(l_concat, p=.5),
            num_units=params['dim_hidden'],
            nonlinearity=lasagne.nonlinearities.rectify
        )

        l_out = lasagne.layers.DenseLayer(
            lasagne.layers.dropout(l_ff, p=.5),
            num_units=params['n_classes'],
            nonlinearity=lasagne.nonlinearities.softmax
        )

        pred = lasagne.layers.get_output(l_out)
        cost = -T.mean(T.log(pred[T.arange(pred.shape[0]), Y]))
        model_params = lasagne.layers.get_all_params(l_out)
        updates = lasagne.updates.adagrad(cost, model_params, params['lr'])

        self.train = theano.function([X, mask, Y], outputs=cost, updates=updates)
        self.predict = theano.function([X, mask], outputs=pred)

        self.l_out = l_out

    def save(self, path_to_save):
        params = lasagne.layers.get_all_param_values(self.l_out)
        cPickle.dump(params, open(path_to_save, 'w'))

    def load(self, path_to_load):
        params = cPickle.load(open(path_to_load, 'r'))
        lasagne.layers.set_all_param_values(self.l_out, params)
