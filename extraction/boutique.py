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

class extract_boutique(object):

    authorized = [
        "JJ","NN","NNS","NN-JJ","JJ-NN","NN-NN","NNS-NNS","NNS-NN","NN-NNS","NNS-JJ","JJ-NNS","NNS-IN-NNS","NN-IN-NN","JJ-IN-NNS","NNS-IN-JJ","JJ-IN-NN","NN-IN-JJ"
    ]

    not_replace = [
        "geo", "nat", "date", "prix", "vente", "femme", "stock", "yo", 
        "sales", "new", "woman", "women", "dior", "for", "le", "shoe"
    ]

    def __init__(self, csv_path, n_max=3):
        self.csv = pd.read_csv(csv_path,names=['Boutique']).dropna()
        print("Cleaning csv ...")
        self.clean_csv()
        self.n_max = n_max

    def removeRowWithSpecialCharacterAndNumbers(self, w):
        pattern = re.compile('^[a-zA-Z-\' ]+$')
        return pattern.match(w) != None

    def remove_wholesale(self, x):
        return not ('Wholesale' in x)

    def removeCityNames(self, x):
        if " - " in x:
            return " "+x.split(" - ")[1].lower().rstrip().lstrip()+" "
        return x.lower()

    def clean_csv(self):
        self.csv = self.csv[self.csv.Boutique.apply(self.removeRowWithSpecialCharacterAndNumbers)]
        self.csv = self.csv[self.csv.Boutique.apply(self.remove_wholesale)]
        self.csv['Boutique'] = self.csv.Boutique.apply(self.removeCityNames)
        self.csv = self.csv.drop_duplicates()
        empties = self.csv['Boutique'] != ""
        self.csv = self.csv[empties]

    def csv_contains(self, w):
        return self.csv[self.csv.Boutique.str.contains(" "+w.rstrip().lstrip()+" ")]

    def get_product(self, sentence):
        return len(self.csv_contains(sentence))>0

    def aggressive_tokenize(self, text):
        min_length = 3
        text = re.sub('[,;?:!.]', '', text);
        words = map(lambda word: word.lower(), text.split(" "));
        return list(words)

    def tag_dict(self, sentence):
        cleaned = " ".join(self.aggressive_tokenize(sentence))
        t = TextBlob(sentence, pos_tagger=PatternTagger(), analyzer=PatternAnalyzer()).tags
        d = dict()
        for a in t:
            d[a[0].lower()] = a[1]
        return d

    def extract(self, sentence):
        results = []
        sentence = sentence.lower()
        tags_dict = self.tag_dict(sentence)
        #print(tags_dict)
        for i in range(1,self.n_max+1):
            results = self.extract_N(sentence, tags_dict, results, i)
        for w in results:
            sentence = sentence.replace(w, "")
        #print('Boutique extracted: ')
        #print(results)
        return (results,sentence)

    def extract_N(self, sentence, tags_dict, prev_results, n):
        prev_results_copy = prev_results[:]
        #print("******** Extracting "+str(n)+"-gram")
        sentence_tokens = self.aggressive_tokenize(sentence)
        #print(sentence_tokens)
        ng = ngrams(sentence_tokens,n)
        ok_products = []
        for item in ng:
            short_sentence = " ".join(item)
            auth = not (len([w for w in self.not_replace if w in short_sentence])>0 or len([w for w in item if w not in tags_dict])>0)
            if auth:
                words_tags = ""
                for itm in item:
                    words_tags += tags_dict[itm]+"-"
                #print(short_sentence+" :: "+words_tags[:-1])
                if words_tags[:-1] in self.authorized:
                    #print(short_sentence+" --")
                    #print(self.csv_contains(short_sentence))
                    if self.get_product(short_sentence):
                        #print("Found: "+short_sentence)
                        ok_products.append(short_sentence)
                        for i in range(len(prev_results_copy)):
                            if prev_results_copy[i] in short_sentence:
                                prev_results_copy[i] = ''
        return ok_products+[a for a in prev_results_copy if a != '']

    def clean_text(self, text):
        copy = text[:].lower()
        to_replace,nothing = self.extract(text)
        for w in to_replace:
            #print("SHOP replacing: "+w)
            copy = copy.replace(w, "SHOP")
        return copy

# itm = extract_boutique('/Users/xav/Desktop/DTY/Dior/rest/data/Boutiques.csv')
# print("Montaigne, Bond Street et Peking Road ont-elles une couverture moyenne de stocks en Sacs Femme supérieure à 3 mois ?")
# print(itm.clean_text("Montaigne, Bond Street et Peking Road ont-elles une couverture moyenne de stocks en Sacs Femme supérieure à 3 mois ?"))
