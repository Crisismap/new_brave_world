import pdb
import gensim
import pandas as pd
import numpy as np

from argparse import ArgumentParser
from nltk.tokenize import word_tokenize
from nltk.stem.snowball import RussianStemmer
from pandas import DataFrame
import scipy.cluster.hierarchy as hcluster
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans, DBSCAN, AffinityPropagation
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA, TruncatedSVD

def handle_args():
    parser = ArgumentParser()
    parser.add_argument("-f", "--fname", default = 'allnews.csv')
    args = parser.parse_args()
    return args

def is_cyrillic(symbol): return ord(symbol)>128
def cyr(some_string): return any(is_cyrillic(s) for s in some_string) and not "the" in some_string.lower()

def make_df(fname = "/Users/fminlos/my_projects/Crisismap_-_all_news/Crisismap - all news.csv", n = 1000):
    df = pd.read_csv(fname, sep= ";", encoding = "utf8")
    df = df[df.type.isin(["ukraine",  "fires", "ecology", "floods"])]
    df["rus"] = df.Description.fillna("").map(cyr)
    df = df[df.rus == True]
    df = df.ix[np.random.permutation(df.index)]
    df = df[:n]
    df["text"] = df.Title + df.Description
    return df

stemmer = RussianStemmer()
analyzer = TfidfVectorizer().build_analyzer()
def stemmed_words(doc):
    return (stemmer.stem(w) for w in analyzer(doc))
stem_vectorizer = TfidfVectorizer(analyzer=stemmed_words)

args = handle_args()
fname = args.fname
df = make_df(fname, n = 300)

tfidf_matrix  =  stem_vectorizer.fit_transform(df.text)

from make_clusters import  cartesian_vectorize
coords = np.column_stack(cartesian_vectorize(df.lat, df.long))

result = np.hstack((tfidf_matrix.toarray(), coords*20))

svd_model = TruncatedSVD()
result = svd_model.fit_transform(result)

model = AffinityPropagation()
df["clusters"] = model.fit_predict(result)

#cluster_sizes = df.groupby("clusters").size()
#print cluster_sizes[cluster_sizes>3].index
#print df[df.clusters.isin(cluster_sizes[cluster_sizes>3].index)].sort("clusters")
