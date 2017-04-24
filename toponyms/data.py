#-*- coding: UTF-8 -*-
import pymorphy2
import numpy as np
import os,csv
import re
import lasagne
np.set_printoptions(threshold='nan')

morph = pymorphy2.MorphAnalyzer()

def grammar_token(token):
    if len(morph.parse(token)) > 0:
        t = reduce(lambda x,y : x + '_' + str(y), sorted(morph.parse(token)[0].tag.grammemes), '')
    else:
        t = token
    return t

def normal_form (token):
    if len(morph.parse(token)) > 0:
        return morph.parse(token)[0].normal_form
    else:
        return token

def iscap(word):
    capitalised = False
    cap = lambda _ : len(_) > 0 and _[0].isupper() and (len(_) == 1 or _[1:].islower())
    if cap(word):
        capitalised = True
    else:
        parts = word.split('-')
        if cap(parts[0]) and all(cap(_) or _.islower() for _ in parts):
            capitalised = True
    return capitalised

def rus_vector(word, model):
    if normal_form(word)  in model.vocab and grammar_token(word) in model.vocab:
        return np.hstack((model[normal_form(word)],model[grammar_token(word)], [iscap(word),]))
    elif grammar_token(word) in model.vocab:
        return np.hstack((model['unk'], model[grammar_token(word)], [iscap(word),]))
    else:
        return np.hstack((model['unk'], np.zeros((model.vector_size, )), [iscap(word),]))

def eng_vector(word, model):
    if word.lower()  in model.vocab :
        return np.concatenate((model[word.lower()], [iscap(word),]))
    else:
        return np.concatenate((model['unk'], [iscap(word),]))

def neurons(words, winsize, model, lang = 'rus'):
    l = len(words)
    words = [u'<fullstop>'] * winsize + words[:-1] + [u'<fullstop>'] * winsize
    if lang == 'rus':
        ns = np.zeros((l - 1, 3, (model.vector_size * 2 + 1)))
        for i in xrange(winsize, l + winsize - 1):
            ns[i - winsize, :, :] = np.vstack((np.mean(tuple(rus_vector(_, model) for _ in  words[i - winsize: i]), axis = 0), rus_vector(words[i], model),
                                                       np.mean(tuple(rus_vector(_, model) for _ in  words[i + 1: i + winsize + 1]), axis = 0)))
    else:
        ns = np.empty((l - 1, 3, (model.vector_size + 1)))
        for i in xrange(winsize, l + winsize - 1):
            ns[i - winsize, :, :] = np.vstack((np.mean(tuple(eng_vector(_, model) for _ in  words[i - winsize: i]), axis = 0), eng_vector(words[i], model),
                                                       np.mean(tuple(eng_vector(_, model) for _ in  words[i + 1: i + winsize + 1]), axis = 0)))
    return ns

def mklsts (CORPUS, files, winsize,  word2vec, lang = 'rus'):
    WORDS, CLS = [], []
    if lang == 'rus':
        Ns = np.empty((0,3, word2vec.vector_size * 2 + 1))
    else:
        Ns = np.empty((0,3, word2vec.vector_size + 1))
    for file in files:

        with open (os.path.join(CORPUS, file), 'r') as f:
            words,cls = [], []
            reader = csv.reader(f, delimiter = '\t')
            for row in reader:
                words.append(row[0].decode('utf-8'))
                cls.append(int(row[1]))
            n = neurons(words, winsize, word2vec, lang = lang)
            WORDS.extend(words)
        CLS.extend(cls[:-1])
        Ns = np.concatenate((Ns, n))


    return Ns,  WORDS, np.asarray(CLS, dtype = 'int32')


def  get_tokens(text): #split to tokens
    text = re.sub(ur'&quot;', ur'"', text)
    text = re.sub(ur'([ ^$][йцукенгшщзхъфывапролджэячсмитьбю0-9a-z]+)([\-])', ur'\1 \2 ', text)
    text = re.sub(ur'([\-])([йцукенгшщзхъфывапролджэячсмитьбю0-9a-z]+)', ur' \1 \2', text)
    #split to sentences
    text = re.sub(ur'[ <>\[\]]', ' ', text)#
    text = re.sub(ur',[ ]*([.!?]+)', ur'<fullstop>', text)
    text = re.sub(ur'([^ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮA-Z])([.!?]+)[ \n]+([ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮA-Z])',ur'\1 <fullstop> \3', text)
    text = re.sub(ur'([^ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮA-Z])([.!?]+)[ ]*$',ur'\1 <fullstop> ', text)
    text = re.sub(ur'([ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮA-Z]+[ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮA-Z]+)([.!?]+)', ur'\1 <fullstop>', text)
    text = re.sub(ur'([\.,:;!\?\=/&\(\)»„“"”«—%])', ur' \1 ', text)
    text = re.sub(ur'([йцукеншгщзхъфывапролджэячсмитьбюЦЙУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ0-9a-zA-Z\+])(["»„\)])', ur'\1 \2', text)
    text = re.sub(ur'([\(“"«])([йцукеншгщзхъфывапролджэячсмитьбюЦЙУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ0-9a-z-A-Z\+])', ur'\1 \2', text)
    text = re.sub(ur'[ ]+', ' ', text)
    words = text.split()
    return words

def del_commas(source):
    text = re.sub(ur'&quot;', ur'"', source)
    text = re.sub(ur'([\.,:;!\?\=\-—/&"»„\)\(“«])', ur' ', text)
    text = re.sub(ur'[ ]+', ' ', text)
    return text

def Pr (result, response):
    try:
        return  len(result.intersection(response))/float(len(result))
    except:
        print 'no true results'
        return 0

def Re (result, response):
    try:
        return len(response.intersection(result))/float(len(response))
    except:
        print 'no true responses'
        return 0

def f1(result, response):
    try:
        return 2 * Pr(result, response) * Re(result, response) / float(Pr (result, response) + Re(result, response) )
    except:
        print 'invalid f1'
        return 0

def scores(result, response):
    precision = Pr (result, response)
    recall = Re (result, response)
    f1 = 2 * precision * recall/float(precision + recall)
    return precision, recall, f1


def build_mlp(shape, input_var=None):

    network = lasagne.layers.InputLayer(shape=shape[0],
                                     input_var=input_var)
    #l_in_drop = lasagne.layers.DropoutLayer(l_in, p=0.2)
    for hid in shape[1:]:
        network = lasagne.layers.DenseLayer(
            network, num_units=hid,
            nonlinearity=lasagne.nonlinearities.sigmoid,
            W=lasagne.init.GlorotUniform())
    #l_hid1_drop = lasagne.layers.DropoutLayer(l_hid1, p=0.5)
    network = lasagne.layers.DenseLayer(
        network, num_units=3,
        nonlinearity=lasagne.nonlinearities.softmax)
    return network

def iterate_minibatches(inputs, targets, batchsize, shuffle=False):

    assert len(inputs) == len(targets)
    if shuffle:
        indices = np.arange(len(inputs))
        np.random.shuffle(indices)
    for start_idx in range(0, len(inputs) - batchsize + 1, batchsize):
        if shuffle:
            excerpt = indices[start_idx:start_idx + batchsize]
        else:
            excerpt = slice(start_idx, start_idx + batchsize)
        yield inputs[excerpt], targets[excerpt]