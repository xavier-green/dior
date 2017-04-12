# -*- coding: utf-8 -*-

import sys
sys.path.append('/usr/local/Cellar/python3/3.6.0/Frameworks/Python.framework/Versions/3.6/lib/python3.6/site-packages')
import pandas as pd
from stop_words import get_stop_words
stop_words_old = get_stop_words('fr')
not_stop_words = ["ou","où","qui","quand","quel","quelle","quelle"]
stop_words = [x for x in stop_words_old if x not in not_stop_words]
import re
from treetaggerpython.treetagger import TreeTagger
tt = TreeTagger(language='french')
from nltk.util import ngrams 

class ProductExtractor(object):
    
    authorized = [
        "ADJ-NOM","NOM-ADJ","ADJ","NOM-ADJ-NOM","NOM","NOM-DET-NOM","ADJ-DET-NOM","NOM-DET-ADJ","NOM-PRP-NOM"
    ]
    
    def __init__(self, csv_path, tree, n_max=3):
        self.csv = pd.read_csv(csv_path,names=['Produit']).dropna()
        print("Cleaning csv ...")
        self.clean_csv()
        self.tree_tagger = tree
        self.n_max = n_max
    
    def removeRowWithSpecialCharacterAndNumbers(self, w):
        pattern = re.compile('^[a-zA-Z-\' ]+$')
        return pattern.match(w) != None
    
    def removShortStrings(self, x):
        return " ".join([w.lower() for w in x.split(" ")if len(w)>2])
    
    def clean_csv(self):
        self.csv = self.csv[self.csv.Produit.apply(self.removeRowWithSpecialCharacterAndNumbers)]
        self.csv['Produit'] = self.csv.Produit.apply(self.removShortStrings)
        self.csv = self.csv.drop_duplicates()
        empties = self.csv['Produit'] != ""
        self.csv = self.csv[empties]
    
    def csv_contains(self, w):
        return self.csv[self.csv.Produit.str.contains(" "+w.rstrip().lstrip()+" ")]
    
    def get_product(self, sentence):
        return len(self.csv_contains(sentence))>0
    
    def extract(self, sentence):
        results = []
        for i in range(1,self.n_max+1):
            results += self.extract_N(sentence, i)
        return results
        
    def extract_N(self, sentence,n):
        print("******** Extracting "+str(n)+"-gram")
        sentence_tokens = sentence.split(" ")
        ng = ngrams(sentence_tokens,n)
        ok_products = []
        for item in ng:
            short_sentence = " ".join(item)
            tags = self.tree_tagger.tag(" ".join(item))
            words_tags = ""
            for tag in tags:
                words_tags += tag[1].split(":")[0]+"-"
            #print(short_sentence+" :: "+words_tags[:-1])
            if words_tags[:-1] in self.authorized:
                #print(short_sentence+" --")
                #print(self.csv_contains(short_sentence))
                if self.get_product(short_sentence):
                    print("Found: "+short_sentence)
                    ok_products.append(short_sentence)
        return ok_products
    
itm = ProductExtractor('/Users/xav/Downloads/products.csv', tt)
print(itm.extract("Combien de rose des vents et de souliers avons-nous vendu la semaine derniere"))