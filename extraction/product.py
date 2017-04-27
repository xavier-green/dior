# -*- coding: utf-8 -*-

import sys
sys.path.append('/usr/local/Cellar/python3/3.6.0/Frameworks/Python.framework/Versions/3.6/lib/python3.6/site-packages')
import pandas as pd
from stop_words import get_stop_words
stop_words_old = get_stop_words('fr')
not_stop_words = ["ou","où","qui","quand","quel","quelle","quelle"]
stop_words = [x for x in stop_words_old if x not in not_stop_words]
import re
from textblob import TextBlob
from textblob_fr import PatternTagger, PatternAnalyzer
from nltk.util import ngrams 

class ProductExtractor(object):
    
    authorized = [
        "JJ","NN","NNS","NN-JJ","JJ-NN","NN-NN","NNS-NNS","NNS-NN","NN-NNS","NNS-JJ","JJ-NNS","NNS-IN-NNS","NN-IN-NN","NN-IN-NNS","JJ-IN-NNS","NNS-IN-JJ","JJ-IN-NN","NN-IN-JJ","NN-NN-NN"
    ]
    
    not_replace = [
        "geo", "nat", "date", "prix", "vente", "stock", "boutique","part", "couleur", "matière", "francais", "moyen", 
        "jours", "couverture", "article", "new", "mix", "type", "cruise", "zone", "clients", "gros", "grands", "top", 
        "nom", "collection", "endroit", "ete", "md", "fp", "mark", "down", "full", "price", "markfown
    ]
    
    def __init__(self, produit_path='data/products.csv', division_path='data/Divisions.csv', departement_path='data/Departements.csv', groupe_path='data/Groupe.csv', theme_path='data/Themes.csv', n_max=3):
        self.produit = pd.read_csv(produit_path,names=['Produit']).dropna().drop_duplicates()
        self.division = pd.read_csv(division_path,names=['Division']).dropna().drop_duplicates()
        self.departement = pd.read_csv(departement_path,names=['Departement']).dropna().drop_duplicates()
        self.groupe = pd.read_csv(groupe_path,names=['Groupe']).dropna().drop_duplicates()
        self.theme = pd.read_csv(theme_path,names=['Theme']).dropna().drop_duplicates()
        print("Cleaning csv ...")
        self.clean_csv()
        self.n_max = n_max
        self.order = {
            "division": {
                "file": self.division,
                "column": self.division.Division
            },
            "departement": {
                "file": self.departement,
                "column": self.departement.Departement
            },
            "groupe": {
                "file": self.groupe,
                "column": self.groupe.Groupe
            },
            "theme": {
                "file": self.theme,
                "column": self.theme.Theme
            },
            "produit": {
                "file": self.produit,
                "column": self.produit.Produit
            }
        }
    
    def removeRowWithSpecialCharacterAndNumbers(self, w):
        pattern = re.compile('^[a-zA-Z-\' ]+$')
        return pattern.match(w) != None
    
    def removShortStrings(self, x):
        return " "+" ".join([w.lower() for w in x.split(" ")if len(w)>2]).rstrip().lstrip()+" "
    
    def clean_product_csv(self):
        self.produit = self.produit[self.produit.Produit.apply(self.removeRowWithSpecialCharacterAndNumbers)]
        self.produit['Produit'] = self.produit.Produit.apply(self.removShortStrings)
        self.produit = self.produit.drop_duplicates()
        empties = self.produit['Produit'] != ""
        self.produit = self.produit[empties]
    
    def low(self, x):
        return " "+x.lower().rstrip().lstrip()+" "
        
    def clean_division_csv(self):
        self.division["Division"] = self.division.Division.apply(self.low)
    
    def clean_departement_csv(self):
        self.departement["Departement"] = self.departement.Departement.apply(self.low)
        
    def clean_groupe_csv(self):
        self.groupe["Groupe"] = self.groupe.Groupe.apply(self.low)
        
    def clean_theme_csv(self):
        self.theme["Theme"] = self.theme.Theme.apply(self.low)
        
    def clean_csv(self):
        self.clean_product_csv()
        self.clean_division_csv()
        self.clean_departement_csv()
        self.clean_groupe_csv()
        self.clean_theme_csv()
    
    def csv_contains(self, w, csv_file, csv_column):
        #print(self.csv[self.csv.Produit.str.contains(" "+w.rstrip().lstrip()+" ")])
        return csv_file[csv_column.str.contains(" "+w.rstrip().lstrip()+" ")]
    
    def get_product(self, sentence, csv_file, csv_column):
        return len(self.csv_contains(sentence, csv_file, csv_column))>0
    
    def aggressive_tokenize(self, text):
        min_length = 3
        words = map(lambda word: word.lower(), text.split(" "));
        p = re.compile('^[a-zA-Z\' ]+$');
        filtered_tokens = list(filter(lambda token:p.match(token) and len(token)>=min_length,words));
        return filtered_tokens

    def tag_dict(self, sentence):
        cleaned = " ".join(self.aggressive_tokenize(sentence))
        t = TextBlob(sentence, pos_tagger=PatternTagger(), analyzer=PatternAnalyzer()).tags
        d = dict()
        for a in t:
            d[a[0].lower()] = a[1]
        return d
    
    def extract(self, sentence):
        results = []
        pattern = re.compile('^[a-zA-Z0-9 ]')
        sentence = sentence.lower()
        sentence = re.sub(r'[^\w\s]','',sentence)
        sentence = " ".join([w for w in sentence.split(" ") if len(w)>=2])
        print("Entry:"+sentence)
        tags_dict = self.tag_dict(sentence)
        #print(tags_dict)
        for i in range(self.n_max,0,-1):
            for key in self.order:
                results, sentence = self.extract_N(sentence, tags_dict, self.order[key], key, results, i)
        return results
        
    def extract_N(self, sentence, tags_dict, csv, bdd, prev_results, n):
        prev_results_copy = prev_results[:]
        sentence_tokens = sentence.split(" ")
        ng = ngrams(sentence_tokens,n)
        ok_products = []
        for item in ng:
            short_sentence = " ".join(item)
            auth = not (len([w for w in self.not_replace if w in short_sentence])>0 or len([w for w in item if w not in tags_dict])>0)
            if auth:
                words_tags = ""
                for itm in item:
                    words_tags += tags_dict[itm]+"-"
                if words_tags[:-1] in self.authorized:
                    #print(short_sentence)
                    if self.get_product(short_sentence, csv["file"], csv["column"]):
                        #print("ok")
                        matched_item = {}
                        matched_item[bdd] = short_sentence
                        ok_products.append(matched_item)
                        for i in range(len(prev_results_copy)):
                            for key in prev_results_copy[i]:
                                if prev_results_copy[i][key] in short_sentence:
                                    prev_results_copy[i] = ''
        for el in ok_products:
            for key in el:
                sentence = sentence.replace(el[key],'')
        return (ok_products+[a for a in prev_results_copy if a != ''],sentence)
    
    def clean_text(self, text):
        copy = text[:].lower()
        to_replace = self.extract(text)
        for w in to_replace:
            print(w)
            for key in w:
                copy = copy.replace(w[key], "ITEM")
        return copy
    
# itm = ProductExtractor()
# print(itm.extract("Combien de rose des vents et de souliers avons-nous vendu la semaine derniere"))