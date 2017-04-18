# coding=utf-8
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'extraction'))
from product import ProductExtractor
from geography import WordClassification
from date import DateExtractor
from boutique import extract_boutique

import numpy as np
from sklearn.pipeline import Pipeline
import sys
import re
sys.path.append('/usr/local/Cellar/python3/3.6.0/Frameworks/Python.framework/Versions/3.6/lib/python3.6/site-packages')
import fasttext
from stop_words import get_stop_words
stop_words_old = get_stop_words('fr')
not_stop_words = ["ou","où","qui","quand","quel","quelle","quelle"]
stop_words = [x for x in stop_words_old if x not in not_stop_words]
from sklearn import neighbors
from sklearn.externals import joblib
from sklearn.feature_extraction.text import TfidfTransformer

def tokenize(text):
    stripped_punctuation = re.sub(r'[-_;,.?!]',' ',text.lower())
    tokens = stripped_punctuation.split(' ')
    cleaned = []
    for token in tokens:
        if token not in stop_words:
            cleaned.append(token)
    #print("left: "+' '.join(str(x) for x in cleaned))
    return cleaned

class Word2VecVectorizer(object):
    def __init__(self, word2vec_model):
        self.word2vec_model = word2vec_model
        self.dim = word2vec_model.dim
    
    def fit(self, X, y):
        return self 

    def transform(self, X):
        return np.array([
            np.mean([self.word2vec_model[w]
                 for w in tokenize(words) if w in self.word2vec_model.words] or
                [np.zeros(self.dim)], axis=0)
            for words in X
        ])

class intentModel(object):

    def __init__(self, fasttext_model):
        self.word2vec_model = fasttext_model
        self.trained_model = None
        self.world = WordClassification(self.word2vec_model)
        self.datex = DateExtractor()
        self.itm = ProductExtractor('data/products.csv')
        self.boutique = extract_boutique('data/Boutiques.csv')

    def remove_variables(self, text):
        without_date = self.datex.extract(text,text=True)
        without_geo = self.world.get_cleaned(without_date)
        without_item = self.itm.clean_text(without_geo)
        without_boutique = self.boutique.clean_text(without_item)
        print(text+" -- "+without_boutique)
        return without_boutique

    def train(self, data, save_file=False):
        X, y = [], []
        for intent in data:
            for exampleLine in data[intent]["examples"]:
                X.append(self.remove_variables(exampleLine))
                y.append(intent)
        X, y = np.array(X), np.array(y)
        print("Done setting up X and y")
        word2vec = Pipeline([
            ("word2vec vectorizer", Word2VecVectorizer(self.word2vec_model)),
            ('tfidf', TfidfTransformer(use_idf=False)),
            ("knn neighbours", neighbors.KNeighborsClassifier(15, weights='distance'))])
        word2vec.fit(X,y)
        self.trained_model = word2vec
        print("Done fitting the model")
        if save_file==True:
            joblib.dump(word2vec, 'data/word2vec_model.pkl')
            print("Done saving it to pickle file")

    def predict(self, question):
        return self.trained_model.predict([self.remove_variables(question)])[0]






