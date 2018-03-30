import theano
import theano.tensor as T
import lasagne
import cPickle


class BiRNN:
    def __init__(self, params, emb_w):
        X = T.imatrix('input')
        target = T.imatrix('target')

        l_in = lasagne.layers.InputLayer(shape=(params['batch_size'], params['max_len']))
        l1 = lasagne.layers.EmbeddingLayer(
            l_in, input_size=params['vocab_size'], output_size=params['dim_emb'], W=emb_w
        )
        l_forward = lasagne.layers.RecurrentLayer(l1, params['dim_hidden'])
        l_backward = lasagne.layers.RecurrentLayer(l1, params['dim_hidden'], backwards=True)
        l_concat = lasagne.layers.ConcatLayer([l_forward, l_backward], axis=2)
        l_out = lasagne.layers.DenseLayer(
            l_concat, num_units=params['max_len'], nonlinearity=lasagne.nonlinearities.sigmoid
        )

        pred = lasagne.layers.get_output(l_out, X)
        cost = T.mean(lasagne.objectives.binary_crossentropy(pred, target))
        model_params = lasagne.layers.get_all_params(l_out)
        updates = lasagne.updates.adagrad(cost, model_params, params['lr'])

        self.train = theano.function([X, target], outputs=cost, updates=updates)
        self.predict = theano.function([X], outputs=pred)

        self.l_out = l_out

    def save(self, path_to_save):
        params = lasagne.layers.get_all_param_values(self.l_out)
        cPickle.dump(params, open(path_to_save, 'w'))

    def load(self, path_to_load):
        params = cPickle.load(open(path_to_load, 'r'))
        lasagne.layers.set_all_param_values(self.l_out, params)
