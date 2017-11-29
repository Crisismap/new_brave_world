#-*- coding: UTF-8 -*-
import theano
import lasagne
import theano.tensor as T
import time
import data
import numpy as np

class NetworkException(Exception):
    pass

from theano.printing import pydotprint
import graphviz
import pydot_ng as pydot


class Engine(object):
    def __init__(self,  input_var, network_creator, args, word2vec, lang, target_var = None, model = None ):
        self.network = network_creator(args, input_var)
        self.fitted = False
        self.input_var = input_var# T.dtensor3('inputs')
        self.target_var = target_var# T.ivector('targets')
        self.word2vec = word2vec
        self.lang = lang

        if not self.target_var is None:
            self.prediction = lasagne.layers.get_output(self.network)
            self.loss = lasagne.objectives.categorical_crossentropy(self.prediction, self.target_var).mean() + 1e-4 * lasagne.regularization.regularize_network_params(
                self.network, lasagne.regularization.l2)

            self.params = lasagne.layers.get_all_params(self.network, trainable=True)
            self.updates = lasagne.updates.nesterov_momentum(self.loss, self.params, learning_rate=0.005, momentum=0.9)
            self.train_fn = theano.function([self.input_var, self.target_var], self.loss, updates=self.updates)
        self.test_prediction = lasagne.layers.get_output(self.network, deterministic=True)
        self.predict_fn = theano.function([self.input_var], T.argmax(self.test_prediction, axis=1),on_unused_input='warn')
        #pydotprint(self.predict_fn, 'examples/mlp.png')
        #theano.printing.pydotprint(self.predict_fn, outfile='examples/mlp.png', var_with_name_simple=True)

        if not model is None:
            #try:
                self.fitted = True
                self.model = model
                with np.load(self.model) as f:
                    param_values = [f['arr_%d' % i] for i in range(len(f.files))]
                    lasagne.layers.set_all_param_values(self.network, param_values)
            #except:
            #     raise  NetworkException('network and model do not match!')




    def fit(self, X_train, y_train, num_epochs, verbatim = True):

            for epoch in range(num_epochs):
                # In each epoch, we do a full pass over the training data:
                train_err = 0
                train_batches = 0
                start_time = time.time()
                for batch in data.iterate_minibatches(X_train, y_train,  100, self.word2vec, lang = self.lang, winsize = 1, shuffle=True):
                    inputs, targets = batch

                    train_err += self.train_fn(inputs, targets)
                    train_batches += 1
                if verbatim:
                    print "Epoch %d of %d took % 3f s" % (epoch + 1, num_epochs, time.time() - start_time)
                    print"  training loss:\t\t%6f" % (train_err / train_batches)

            self.fitted = True


    def predict(self, X_test):
        if self.fitted:
            return list(self.predict_fn(X_test))
        else:
            raise NetworkException('Network is not fitted!')

    def setmodel(self, model):
        self.model = model
        self.fitted = True

        with np.load(self.model) as f:
            param_values = [f['arr_%d' % i] for i in range(len(f.files))]
            lasagne.layers.set_all_param_values(self.network, param_values)





