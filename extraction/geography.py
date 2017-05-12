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

def getWord2vecVector(word):
    if word.strip() != "":
        # print("Getting vector for "+word)
        url = "vps397505.ovh.net/"+word
        url = quote(url.encode('utf8'))
        vec = urlopen("http://"+url).read()
        return [float(x) for x in vec.decode("utf-8").replace("[\n  ","").replace("\n]\n","").split(", \n  ")]
    return np.zeros(300)

class WordClassification(object):

    def __init__(self, threshold=0.14, uzone_path='../data/uzone.csv', zone_path='../data/zone.csv', 
        subzone_path='../data/szone.csv', country_path='../data/country.csv', state_path='../data/state.csv'):

        self.cities = ["Paris","London","Tokyo","NewYork","Seoul","Dubai","Madrid","Ginza"]
        self.countries = ["EtatsUnis","Espagne","Japon","Chine","France","Emirats","Suisse","Amerique", "Asia", "Asie", "Europe", "Etats Unis"]
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
                "column": self.uzone.Uzone
            }},
            {"zone": {
                "file": self.zone,
                "column": self.zone.Zone
            }},
            {"subzone": {
                "file": self.subzone,
                "column": self.subzone.Subzone
            }},
            {"country": {
                "file": self.count,
                "column": self.count.Country
            }},
            {"state": {
                "file": self.state,
                "column": self.state.State
            }}
        ]
        print("Cleaning csv ...")
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
    
    def get_product(self, sentence, csv_file, csv_column):
        return len(self.csv_contains(sentence, csv_file, csv_column))>0
        
    def cos(self, a, b):
        return np.dot(a,b)/(np.linalg.norm(a)*np.linalg.norm(b))
    
    def tokenize(self, text):
        #stripped_punctuation = re.sub(r'[-_;,.?!]',' ',text.lower())
        tokens = text.split(' ')
        cleaned = []
        for token in tokens:
            cleaned.append(token)
        return cleaned
    
    def find_similar(self,similar_classed,text):
        
        total_comparison_corpus = similar_classed

        C = np.zeros((len(total_comparison_corpus),300))

        for idx, term in enumerate(total_comparison_corpus):
            C[idx,:] = getWord2vecVector(term)
        #print(C)


        tokens = self.tokenize(text)
        scores = [0.] * len(tokens)
        found=[]

        for idx, term in enumerate(tokens):
            vec = getWord2vecVector(term)
            cosines = self.cos(C,vec)
            score = np.mean(cosines)
            print(term,"=",score)
            scores[idx] = score
            if (score > self.threshold):
                found += self.match_in_csv(term)
                #found.append({term: score})

        return found

    def match_in_csv(self, term):
        print("match for",term,"?")
        for category in self.order:
            for key in category:
                if self.get_product(term, category[key]["file"], category[key]["column"]):
                    print(term," se trouve bien dans ",key)
                    return [(key,term)]
        return []
    
    def find_similar_city(self, text):
        return self.find_similar(self.cities,text)
    def find_similar_country(self, text):
        return self.find_similar(self.countries,text)
    def find_similar_nationality(self, text):
        return self.find_similar(self.nationalities,text)

    def get_cleaned(self,text):
        result = self.find_similar_city(text)+self.find_similar_country(text)
        cloned_text = '%s' % text
        for table,element in result:
            print("GEO replacing: "+element)
            cloned_text = cloned_text.replace(element,"GEO")

        result = self.find_similar_nationality(text)
        for table,element in result:
            print("NAT replacing: "+element)
            cloned_text = cloned_text.replace(element,"NAT")
        #print("cleaned text: ",cloned_text)
        return cloned_text
    
    def find_similar_words(self, text):
        # json = {
        #     "cities": self.find_similar_city(text),
        #     "countries": self.find_similar_country(text),
        #     "nationalities": self.find_similar_nationality(text)
        # }
        json = self.find_similar_city(text)+self.find_similar_country(text)+self.find_similar_nationality(text)
        for table,word in json:
            text = text.replace(word,'')
        return (json,text)

world = WordClassification()
print(world.find_similar_words("La semaine dernière, qui a conclu le plus de ventes en america"))
# print(world.find_similar_words("Les américains achètent-ils plus que les japonais"))
# print(world.find_similar_words("Quelle part de russes dans les achats de Lady Dior"))
# print(world.find_similar_words("Cette semaine, combien y a-t-il eu de clients marocains"))
# print(world.find_similar_words("Est-ce que la plupart des clients au Moyen Orient sont locaux"))







