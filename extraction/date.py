# coding=utf8

import re
import unicodedata
import sys
sys.path.append('/usr/local/Cellar/python3/3.6.0/Frameworks/Python.framework/Versions/3.6/lib/python3.6/site-packages')

jours = ["Lundi","Lu","Lun","Mardi","Mercredi","Mer","Me","Jeudi","Jeu","Je","Vendredi","Ven","Ve","Samedi","Sam","Sa","Dimanche","Dim","Di"]
mois = ["Janvier","Janv","Jan","Février","Févr","Fév","Mars","Avril","Avr","Mai","Juin","Jun","Juillet","Juil","Jul","Août","Aoû","Septembre","Sept","Sep","Octobre","Oct","Novembre","Nov","Décembre","Déc"]
date_words = ["mois","semaine","semaines","année","années","annee","annees","an","jour","jours","trimestre","semestre","hier","avant-hier","aujourd'hui"]
previous_words = ["il y a","depuis","ce","cette","dernier","derniers","derniere"]
post_words = ["dernier","derniers","derniere","dernière"]

class DateExtractor(object):

    def clean(self,text):
        #print(text)
        #search_string = ''.join((c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn'))
        stripped_punctuation = re.sub(r'[-_;,.?!]',' ',text.lower())
        tokens = stripped_punctuation.split(' ')
        cleaned = []
        for token in tokens:
            cleaned.append(token)
        #print("left: "+' '.join(str(x) for x in cleaned))
        return cleaned

    def getPreviousWord(self,current_index,sentence):
        if current_index>0:
            previous_word = sentence[current_index-1]
            if (previous_word in previous_words):
                return self.getPreviousWord(current_index-1,sentence)+[previous_word]
            elif previous_word.isdigit():
                return [previous_word]
        return []

    def getPostWord(self,current_index,sentence_length,sentence):
        if (current_index+1)<sentence_length:
            post_word = sentence[current_index+1]
            if post_word in post_words:
                return [post_word]
        return []

    def extract(self,sentence,text=False):
        sentence_split = self.clean(sentence)#.split(" ")
        #print(sentence_split)
        sentence_length = len(sentence_split)
        date_part,date_string = [],"abcdefghijklmnopqrstuvw"
        allDates = []
        for date_word in date_words:
            try:
                date_word_index = sentence_split.index(date_word)
                previousWord = self.getPreviousWord(date_word_index, sentence_split)
                postWord = self.getPostWord(date_word_index,sentence_length,sentence_split)
                date_part = previousWord+[sentence_split[date_word_index]]+postWord
                #print(date_part)
                date_string = " ".join(date_part)
                allDates.append(date_string)
                #print("{} : {}".format(date_string,output))
            except:
                pass
        if text:
            return " ".join(sentence_split).replace(date_string,"DATE").rstrip()
        return allDates


# datex = DateExtractor()
# print(datex.extract("La semaine dernière, qui a conclu le plus de ventes à Ginza"))

