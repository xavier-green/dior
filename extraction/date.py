# coding=utf8

import re
import unicodedata
import sys
sys.path.append('/usr/local/Cellar/python3/3.6.0/Frameworks/Python.framework/Versions/3.6/lib/python3.6/site-packages')
import datetime

jours = ["Lundi","Lu","Lun","Mardi","Mercredi","Mer","Me","Jeudi","Jeu","Je","Vendredi","Ven","Ve","Samedi","Sam","Sa","Dimanche","Dim","Di"]
mois = ["Janvier","Janv","Jan","Février","Févr","Fév","Mars","Avril","Avr","Mai","Juin","Jun","Juillet","Juil","Jul","Août","Aoû","Septembre","Sept","Sep","Octobre","Oct","Novembre","Nov","Décembre","Déc"]
date_words = {
    "mois":-30,
    "semaine":-7,
    "semaines":-7,
    "année":-365,
    "années":-365,
    "an":-365,
    "jour":-1,
    "jours":-1,
    "trimestre":-90,
    "semestre":-120,
    "hier":-1,
    "avant-hier":-2,
    "aujourd'hui":0
}
previous_words = ["il y a","depuis","ce","cette","dernier","derniers","derniere","dernieres"]
post_words = ["dernier","derniers","derniere","dernière"]

chiffres = {
    "un":1,
    "deux":2,
    "trois":3,
    "quatre":4,
    "cinq":5,
    "six":6,
    "sept":7,
    "huit":8,
    "neuf":9,
    "dix":10,
    "quinze":15,
    "vingt":20
}

class DateExtractor(object):

    def clean(self,text):
        #print(text)
        stripped_punctuation = re.sub(r'[-_;,.?!]',' ',text.lower().replace("'", " "))
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
            elif previous_word in chiffres:
                return [chiffres[previous_word]]
            elif previous_word.isdigit():
                return [previous_word]

        return []

    def getPostWord(self,current_index,sentence_length,sentence):
        if (current_index+1)<sentence_length:
            post_word = sentence[current_index+1]
            if post_word in post_words:
                return [post_word]
        return []

    def getPreviousAmount(self,current_index,sentence):
        if current_index>0:
            previous_word = sentence[current_index-1]
            if (previous_word in previous_words):
                return self.getPreviousAmount(current_index-1,sentence)
            elif previous_word.isdigit():
                return previous_word
        return 1

    def get_new_date(self,dateFormat="%Y%m%d", addDays=0):
        timeNow = datetime.datetime(2017, 3, 4, 12, 00)
        if (addDays!=0):
            anotherTime = timeNow + datetime.timedelta(days=addDays)
        else:
            anotherTime = timeNow
        return anotherTime.strftime(dateFormat)

    def extract_numerical(self,sentence,text=False):
        sentence_split = self.clean(sentence)#.split(" ")
        sentence_length = len(sentence_split)
        date_part,date_string = [],"abcdefghijklmnopqrstuvw"
        allDates = []
        for date_word in date_words:
            try:
                date_word_index = sentence_split.index(date_word)
                days_diff = int(date_words[date_word])
                days_diff_amount = int(self.getPreviousAmount(date_word_index, sentence_split))
                #print("{} : {}".format(days_diff,days_diff_amount))
                total_days = days_diff*days_diff_amount
                #print("Total days "+str(total_days))
                new_date = self.get_new_date(addDays=total_days)
                allDates.append(new_date)
            except:
                pass
        return allDates

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
        return (allDates, " ".join(sentence_split).replace(date_string,"").rstrip())


# datex = DateExtractor()
# print(datex.extract_numerical("La semaine dernière, qui a conclu le plus de ventes à Ginza"))
