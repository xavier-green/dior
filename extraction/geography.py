# -*- coding: utf-8 -*-

import sys
sys.path.append('/usr/local/Cellar/python3/3.6.0/Frameworks/Python.framework/Versions/3.6/lib/python3.6/site-packages')
import numpy as np
import re
import pandas as pd
from stop_words import get_stop_words
stop_words_old = get_stop_words('fr')
not_stop_words = ["ou","où","qui","quand","quel","quelle","quelle"]
stop_words = [x for x in stop_words_old if x not in not_stop_words]
from textblob import TextBlob
from textblob_fr import PatternTagger, PatternAnalyzer
from nltk.util import ngrams

from urllib.request import quote
from urllib.request import urlopen
import json
import requests

cache_corpus = {}

def getWord2vecVector(words):
    headers = {'content-type': "application/json",'cache-control': "no-cache"}
    url = "http://vps397505.ovh.net/"
    post_fields = {'words':[w.lower() for w in words]}
    post_fields = json.dumps(post_fields)
    # print(post_fields);
    response = requests.request("POST", url, data=post_fields, headers=headers)
    word_vec = response.text.replace("[\n  [\n    ","").replace("\n  ]\n]\n","").split("\n  ], \n  [\n")
    final_vec = []
    for word_v in word_vec:
        final_vec.append([float(x) for x in word_v.split(", \n    ")])
    return final_vec

class WordClassification(object):

    def __init__(self, threshold=0.12, uzone_path='data/uzone.csv', zone_path='data/zone.csv', 
        subzone_path='data/szone.csv', country_path='data/country.csv', state_path='data/state.csv'):

        self.cities = ["Paris","London","Tokyo","NewYork","Seoul","Dubai","Madrid","Ginza"]
        self.countries = ["EtatsUnis","Espagne","Japon","Chine","France","Emirats","Suisse","Amerique", "Asia", "Asie", "europe", "Etats Unis"]
        self.nationalities = ["Russe","Francais","Americain","Chinois"]
        self.threshold = threshold

        self.uzone = pd.read_csv(uzone_path,names=['Uzone']).dropna().drop_duplicates()
        self.zone = pd.read_csv(zone_path,names=['Zone']).dropna().drop_duplicates()
        self.count = pd.read_csv(country_path,names=['Country']).dropna().drop_duplicates()
        self.subzone = pd.read_csv(subzone_path,names=['Subzone']).dropna().drop_duplicates()
        self.state = pd.read_csv(state_path,names=['State']).dropna().drop_duplicates()
        
        self.order = [
            {"uzone": {
                "file": self.uzone,
                "column": self.uzone.Uzone,
                "single": 'Uzone'
            }},
            {"zone": {
                "file": self.zone,
                "column": self.zone.Zone,
                "single": 'Zone'
            }},
            {"subzone": {
                "file": self.subzone,
                "column": self.subzone.Subzone,
                "single": 'Subzone'
            }},
            {"country": {
                "file": self.count,
                "column": self.count.Country,
                "single": 'Country'
            }},
            {"state": {
                "file": self.state,
                "column": self.state.State,
                "single": 'State'
            }}
        ]
        # print("Cleaning csv ...")
        self.clean_csv()

    def removeRowWithSpecialCharacterAndNumbers(self, w):
        pattern = re.compile('^[a-zA-Z-\' ]+$')
        return pattern.match(w) != None
    
    def removShortStrings(self, x):
        return " "+" ".join([w.lower() for w in x.split(" ")if len(w)>2]).rstrip().lstrip()+" "
    
    def low(self, x):
        return " "+x.lower().rstrip().lstrip()+" "

    def cleaned_csv(self, file, column):
        file = file[column.apply(self.removeRowWithSpecialCharacterAndNumbers)]
        column = column.apply(self.removShortStrings)
        column = column.apply(self.low)
        file = file.drop_duplicates()
        empties = column != ""
        file = file[empties]
        return file,column
        
    def clean_csv(self):

        for item_category in self.order:
            for key in item_category:
                file = item_category[key]["file"]
                column = item_category[key]["column"]
                item_category[key]["file"],item_category[key]["column"] = self.cleaned_csv(file, column)

    def csv_contains(self, w, csv_file, csv_column):
        return csv_file[csv_column.str.contains(" "+w.rstrip().lstrip()+" ")]
    
    def get_product(self, sentence, csv_file, csv_column, single_column):
        csv_matches = self.csv_contains(sentence, csv_file, csv_column)
        if len(csv_matches)>0:
            return csv_matches[single_column].iloc[0]
        return None
        
    def cos(self, a, b):
        return np.dot(a,b)/(np.linalg.norm(a)*np.linalg.norm(b))
    
    def tokenize(self, text):
        stripped_punctuation = re.sub(r'[-_;,.?!]',' ',text.lower())
        tokens = stripped_punctuation.split(' ')
        cleaned = []
        for token in tokens:
            cleaned.append(token)
        return cleaned
    
    def find_similar(self,similar_classed,text):
        
        total_comparison_corpus = similar_classed

        C = np.zeros((len(total_comparison_corpus),300))

        if similar_classed[0] in cache_corpus:
            print("Found corpus in cache")
            corpus_vectors = cache_corpus[similar_classed[0]]
        else:
            corpus_vectors = getWord2vecVector(total_comparison_corpus)
            cache_corpus[similar_classed[0]] = corpus_vectors

        for idx, vec in enumerate(corpus_vectors):
            C[idx,:] = vec
        #print(C)


        tokens = self.tokenize(text)
        scores = [0.] * len(tokens)
        found=[]
        toreplace = []

        token_vecs = getWord2vecVector(tokens)

        for idx, vec in enumerate(token_vecs):
            cosines = self.cos(C,vec)
            score = np.mean(cosines)
            # print(tokens[idx],"=",score)
            scores[idx] = score
            if (score > self.threshold):
                found += self.match_in_csv(tokens[idx])
                toreplace.append(tokens[idx])
                #found.append({term: score})

        return (found,toreplace)

    def match_in_csv(self, term):
        for category in self.order:
            for key in category:
                matched_geo = self.get_product(term, category[key]["file"], category[key]["column"], category[key]["single"])
                if matched_geo:
                    print(term," se trouve bien dans ",key)
                    return [(key,matched_geo)]
        return []
    
    def find_similar_city(self, text):
        return self.find_similar(self.cities,text)
    def find_similar_country(self, text):
        return self.find_similar(self.countries,text)
    def find_similar_nationality(self, text):
        return self.find_similar(self.nationalities,text)

    def get_cleaned(self,text):
        json,toreplace = self.find_similar_city(text)
        countries_json,countries_replace = self.find_similar_country(text)
        json += countries_json
        toreplace += countries_replace
        cloned_text = '%s' % text
        for element in toreplace:
            print("GEO replacing: "+element)
            cloned_text = cloned_text.replace(element,"GEO")

        json,toreplace = self.find_similar_nationality(text)
        for element in toreplace:
            print("NAT replacing: "+element)
            cloned_text = cloned_text.replace(element,"NAT")
        #print("cleaned text: ",cloned_text)
        return cloned_text
    
    def find_similar_words(self, text):
        json,toreplace = self.find_similar_city(text)
        countries_json,countries_replace = self.find_similar_country(text)
        nationalities_json,nationalities_replace = self.find_similar_nationality(text)
        json += countries_json+nationalities_json
        toreplace += countries_replace+nationalities_replace
        json = list(set(json))
        for word in toreplace:
            text = text.replace(word,'')
        return (json,text)

# world = WordClassification()
# print(world.find_similar_words("La semaine dernière, qui a conclu le plus de ventes en europe, paris"))







