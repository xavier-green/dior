# -*- coding: utf-8 -*-

import sys
sys.path.append('/usr/local/Cellar/python3/3.6.0/Frameworks/Python.framework/Versions/3.6/lib/python3.6/site-packages')
# import fasttext
# model_fasttext_path = '/Users/xav/Downloads/wiki.fr/wiki.fr.bin'
# model_fasttext = fasttext.load_model(model_fasttext_path)
import numpy as np
import re

class WordClassification(object):
    
    def __init__(self, word2vec_model, threshold=0.14):
        self.cities = ["Paris","London","Tokyo","NewYork","Seoul","Dubai","Madrid","Ginza"]
        self.countries = ["EtatsUnis","Espagne","Japon","Chine","France","Emirats","Suisse","Amerique"]
        self.nationalities = ["Russe","Francais","Americain","Chinois"]
        self.word2vec_model = word2vec_model
        self.threshold = threshold
        
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

        C = np.zeros((len(total_comparison_corpus),self.word2vec_model.dim))

        for idx, term in enumerate(total_comparison_corpus):
            if term.lower() in self.word2vec_model.words:
                C[idx,:] = self.word2vec_model[term.lower()]
        #print(C)


        tokens = self.tokenize(text)
        scores = [0.] * len(tokens)
        found=[]

        for idx, term in enumerate(tokens):
            if term in self.word2vec_model.words:
                vec = self.word2vec_model[term]
                cosines = self.cos(C,vec)
                score = np.mean(cosines)
                #print(score)
                scores[idx] = score
                if (score > self.threshold):
                    found.append(term)
                    #found.append({term: score})

        return found
    
    def find_similar_city(self, text):
        return self.find_similar(self.cities,text)
    def find_similar_country(self, text):
        return self.find_similar(self.countries,text)
    def find_similar_nationality(self, text):
        return self.find_similar(self.nationalities,text)

    def get_cleaned(self,text):
        result = self.find_similar_city(text)+self.find_similar_country(text)
        cloned_text = '%s' % text
        for element in result:
            print("GEO replacing: "+element)
            cloned_text = cloned_text.replace(element,"GEO")

        result = self.find_similar_nationality(text)
        for element in result:
            print("NAT replacing: "+element)
            cloned_text = cloned_text.replace(element,"NAT")
        #print("cleaned text: ",cloned_text)
        return cloned_text
    
    def find_similar_words(self, text):
        json = {
            "cities": self.find_similar_city(text),
            "countries": self.find_similar_country(text),
            "nationalities": self.find_similar_nationality(text)
        }
        for key in json:
            for word in json[key]:
                text = text.replace(word,'')
        return (json,text)


# world = WordClassification(model_fasttext)
# print(world.find_similar_words("La semaine dernière, qui a conclu le plus de ventes à madrid"))
# print(world.find_similar_words("Les américains achètent-ils plus que les japonais"))
# print(world.find_similar_words("Quelle part de russes dans les achats de Lady Dior"))
# print(world.find_similar_words("Cette semaine, combien y a-t-il eu de clients marocains"))
# print(world.find_similar_words("Est-ce que la plupart des clients au Moyen Orient sont locaux"))







