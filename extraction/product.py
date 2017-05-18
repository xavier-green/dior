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
        "nom", "collection", "endroit", "ete", "md", "fp", "mark", "down", "full", "price", "markdown", "fullprice",
        "net", "sale", "division", "pays", "tu"
    ]

    def __init__(self, produit_path='data/products.csv', division_path='data/Divisions.csv',
        departement_path='data/Departements.csv', groupe_path='data/Groupe.csv', theme_path='data/Themes.csv',
        family_path='data/family.csv', color_path='data/color.csv', material_path='data/material.csv',
        shape_path='data/shape.csv', n_max=4):

        self.produit = pd.read_csv(produit_path,names=['Produit']).dropna().drop_duplicates()
        self.division = pd.read_csv(division_path,names=['Division']).dropna().drop_duplicates()
        self.departement = pd.read_csv(departement_path,names=['Departement']).dropna().drop_duplicates()
        self.groupe = pd.read_csv(groupe_path,names=['Groupe']).dropna().drop_duplicates()
        self.theme = pd.read_csv(theme_path,names=['Theme']).dropna().drop_duplicates()
        self.famille = pd.read_csv(family_path,names=['Famille']).dropna().drop_duplicates()
        self.color = pd.read_csv(color_path,names=['Color']).dropna().drop_duplicates()
        self.material = pd.read_csv(material_path,names=['Material']).dropna().drop_duplicates()
        self.shape = pd.read_csv(shape_path,names=['Shape']).dropna().drop_duplicates()
        self.order = [
            {"division": {
                "file": self.division,
                "column": self.division.Division,
                "single": 'Division'
            }},
            {"departement": {
                "file": self.departement,
                "column": self.departement.Departement,
                "single": 'Departement'
            }},
            {"famille": {
                "file": self.famille,
                "column": self.famille.Famille,
                "single": 'Famille'
            }},
            {"color": {
                "file": self.color,
                "column": self.color.Color,
                "single": 'Color'
            }},
            {"groupe": {
                "file": self.groupe,
                "column": self.groupe.Groupe,
                "single": 'Groupe'
            }},
            {"material": {
                "file": self.material,
                "column": self.material.Material,
                "single": 'Material'
            }},
            {"shape": {
                "file": self.shape,
                "column": self.shape.Shape,
                "single": 'Shape'
            }},
            {"theme": {
                "file": self.theme,
                "column": self.theme.Theme,
                "single": 'Theme'
            }},
            {"produit": {
                "file": self.produit,
                "column": self.produit.Produit,
                "single": 'Produit'
            }}
        ]
        print("Cleaning csv ...")
        self.clean_csv()
        self.n_max = n_max

    def removeRowWithSpecialCharacterAndNumbers(self, w):
        pattern = re.compile('^[a-zA-Z-\' ]+$')
        return pattern.match(w) != None

    def removShortStrings(self, x):
        return " "+" ".join([w.lower() for w in x.split(" ")if len(w)>1]).rstrip().lstrip()+" "

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

    def get_product(self, sentence, csv_file, csv_column, csv_single):
        csv_matches = self.csv_contains(sentence, csv_file, csv_column)
        if len(csv_matches)>0:
            print(csv_matches)
            return list(csv_matches[csv_single])
        return None

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
        sources = []
        pattern = re.compile('^[a-zA-Z0-9 ]')
        sentence = sentence.lower()
        sentence = re.sub(r'[^\w\s]','',sentence)
        sentence = " ".join([w for w in sentence.split(" ") if len(w)>=2])
        # print("Entry:"+sentence)
        tags_dict = self.tag_dict(sentence)
        #print(tags_dict)
        for i in range(self.n_max,0,-1):
            # print("extraction des "+str(i)+"-gram")
            for orde in self.order:
                for key in orde:
                    # print("extraction en cours pour "+key)
                    results, sentence, sources = self.extract_N(sentence, tags_dict, orde[key], key, results, sources, i)
        print("$$$$$$$$$$$$$ Sources")
        print(sources)
        return (results, sources)

    def extract_N(self, sentence, tags_dict, csv, bdd, prev_results, prev_sources, n):
        prev_results_copy = prev_results[:]
        prev_sources_copy = prev_sources[:]
        sentence_tokens = sentence.split(" ")
        ng = ngrams(sentence_tokens,n)
        ok_products = []
        sources = []
        for item in ng:
            short_sentence = " ".join(item)
            auth = not (len([w for w in self.not_replace if w in short_sentence])>0 or len([w for w in item if w not in tags_dict])>0)
            if auth:
                words_tags = ""
                for itm in item:
                    words_tags += tags_dict[itm]+"-"
                if words_tags[:-1] in self.authorized:
                    #print(short_sentence)
                    #print("getting product for "+str(csv))
                    products_matched = self.get_product(short_sentence, csv["file"], csv["column"], csv["single"])
                    if products_matched:
                        print("Products matched",products_matched)
                        matched_item = {}
                        matched_item[bdd] = short_sentence
                        ok_products.append(matched_item)
                        sources.append((bdd,products_matched))
                        for i in range(len(prev_results_copy)):
                            for key in prev_results_copy[i]:
                                if prev_results_copy[i][key] in short_sentence:
                                    prev_results_copy[i] = ''
        for el in ok_products:
            for key in el:
                sentence = sentence.replace(el[key],'')
        for idx,a in enumerate(prev_results_copy):
            if a != '':
                ok_products.append(a)
                sources.append(prev_sources_copy[idx])
        return (ok_products,sentence, sources)

    def clean_text(self, text):
        copy = text[:].lower()
        to_replace,sources = self.extract(text)
        for w in to_replace:
            print(w)
            for key in w:
                copy = copy.replace(w[key], "ITEM")
        return copy


#itm = ProductExtractor()
#itm = ProductExtractor(
#    produit_path='/Users/xav/Downloads/products.csv',
#    division_path='/Users/xav/Desktop/DTY/Dior/rest/data/Divisions.csv',
#    departement_path='/Users/xav/Desktop/DTY/Dior/rest/data/Departements.csv',
#    groupe_path='/Users/xav/Desktop/DTY/Dior/rest/data/Groupe.csv',
#    theme_path='/Users/xav/Desktop/DTY/Dior/rest/data/Themes.csv',
#    family_path='/Users/xav/Desktop/DTY/Dior/rest/data/family.csv',
#    color_path='/Users/xav/Desktop/DTY/Dior/rest/data/color.csv',
#    material_path='/Users/xav/Desktop/DTY/Dior/rest/data/material.csv',
#    shape_path='/Users/xav/Desktop/DTY/Dior/rest/data/shape.csv')
#print(itm.extract("combien de bags en croco avons nous vendu depuis"))
