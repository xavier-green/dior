# coding=utf-8
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'extraction'))
sys.path.insert(0,'..')
from product import ProductExtractor
from geography import WordClassification
from date import DateExtractor
from boutique import extract_boutique

import numpy as np
from sklearn.pipeline import Pipeline
import sys
import re

from stop_words import get_stop_words
stop_words_old = get_stop_words('fr')
not_stop_words = ["ou","où","qui","quand","quel","quelle","quelle"]
stop_words = [x for x in stop_words_old if x not in not_stop_words]
from sklearn import neighbors
from sklearn.externals import joblib
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.svm import SVC

import json
import requests
import config

def tokenize(text):
    stripped_punctuation = re.sub(r'[-_;,.?!]',' ',text.lower())
    tokens = stripped_punctuation.split(' ')
    cleaned = []
    for token in tokens:
        if token not in stop_words:
            cleaned.append(token)
    #print("left: "+' '.join(str(x) for x in cleaned))
    return cleaned

def getWord2vecVector(words):
    headers = {'content-type': "application/json",'cache-control': "no-cache"}
    url = config.fasttext_url
    post_fields = {'words':[w.lower() for w in words]}
    post_fields = json.dumps(post_fields)
    # print(post_fields);
    response = requests.request("POST", url, data=post_fields, headers=headers)
    word_vec = response.text.replace("[\n  [\n    ","").replace("\n  ]\n]\n","").split("\n  ], \n  [\n")
    final_vec = []
    for word_v in word_vec:
        final_vec.append([float(x) for x in word_v.split(", \n    ")])
    return final_vec

class Word2VecVectorizer(object):

    def __init__(self):
        print("Word2VecVectorizer class")
    
    def fit(self, X, y):
        return self

    def transform(self, X):
        return np.array([
            np.mean(getWord2vecVector(tokenize(words)), axis=0)
            for words in X
        ])

class intentModel(object):

    def __init__(self):
        print("importing geo extractor")
        self.world = WordClassification()
        print("importing date extractor")
        self.datex = DateExtractor()
        print("importing item extractor")
        self.itm = ProductExtractor()
        print("importing boutique extractor")
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
            ("word2vec vectorizer", Word2VecVectorizer()),
            ('tfidf', TfidfTransformer(use_idf=False)),
            ('SVM',SVC(kernel="linear"))])
            # ("knn neighbours", neighbors.KNeighborsClassifier(15, weights='distance'))])
        word2vec.fit(X,y)
        self.trained_model = word2vec
        print("Done fitting the model")
        if save_file==True:
            joblib.dump(word2vec, 'data/word2vec_model.pkl')
            print("Done saving it to pickle file")

    def predict(self, question):
        return self.trained_model.predict([self.remove_variables(question)])[0]






