# coding=utf8

import re
import unicodedata
import sys
sys.path.append('/usr/local/Cellar/python3/3.6.0/Frameworks/Python.framework/Versions/3.6/lib/python3.6/site-packages')
import datetime
import time
from calendar import monthrange

jours = ["Lundi","Lu","Lun","Mardi","Mercredi","Mer","Me","Jeudi","Jeu","Je","Vendredi","Ven","Ve","Samedi","Sam","Sa","Dimanche","Dim","Di"]
mois = ["Janvier","Janv","Jan","Février","Févr","Fév","Mars","Avril","Avr","Mai","Juin","Jun","Juillet","Juil","Jul","Août","Aoû","Septembre","Sept","Sep","Octobre","Oct","Novembre","Nov","Décembre","Déc"]
day_words = {
    "jour":1,
    "jours":1,
    "hier":1,
    "avant-hier":2,
    "aujourd'hui":0,
    "day":1,
    "today":0,
    "yesterday":1,
    "day before yesterday":2,
    "daily":1
}
year_words = {
    "année":1,
    "années":1,
    "annee":1,
    "annees":1,
    "an":1,
    "ans":1,
    "ytd":-1,
    "year":1,
    "years":1,
    "yearly":1,
}
month_words = {
    "mois":1,
    "trimestre":3,
    "trimestres":3,
    "semestre":6,
    "semestres":6,
    "mtd":-1,
    "month":1,
    "months":1,
    "quarter":3,
    "semester":6
}
week_words = {
    "week":1,
    "weeks":1
    "semaine":1,
    "semaines":1,
    "wtd":-1
}
previous_words = ["il y a","depuis","ce","cette","dernier","derniers","derniere","dernieres", "last", "previous"]
post_words = ["dernier","derniers","derniere","dernière", "précédente", "précédent", "precedente", "precedent", "last"]

chiffres = {
    "un":1,
    "one":1,
    "deux":2,
    "two":2,
    "trois":3,
    "three":3,
    "quatre":4,
    "four":4,
    "cinq":5,
    "five":5,
    "six":6,
    "sept":7,
    "seven":7,
    "huit":8,
    "height":8,
    "neuf":9,
    "nine":9,
    "dix":10,
    "ten":10,
    "quinze":15,
    "vingt":20
}

date_words = {
    "mois":-30,
    "month":-30,
    "semaine":-7,
    "semaines":-7,
    "week":-7,
    "année":-365,
    "années":-365,
    "annee":-365,
    "annees":-365,
    "an":-365,
    "ans":-365,
    "year":-365,
    "jour":-1,
    "jours":-1,
    "day":-1,
    "trimestre":-90,
    "quarter":-90,
    "semestre":-180,
    "semestres":-180,
    "semester":-180,
    "hier":-1,
    "yesterday":-1,
    "avant-hier":-2,
    "aujourd'hui":0,
    "today":0
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

    def getPrevious(self, date_string, minus, dateFormat="%Y%m%d"):
        current_date = datetime.datetime.strptime(date_string, dateFormat)
        previous_date = current_date + datetime.timedelta(days=minus)
        return previous_date.strftime(dateFormat)

    def getCurrentDate(self):
        return {
            "day": int(time.strftime("%d")),
            "week": int(time.strftime("%W")),
            "month": int(time.strftime("%m")),
            "year": int(time.strftime("%Y")),
        }

    def annee(self,remove=1,dateFormat="%Y%m%d",toDate=False):
        currentDate = self.getCurrentDate()
        newYear = currentDate["year"] - remove
        startDate = datetime.datetime(newYear, 1, 1, 12, 00)
        startDate = startDate.strftime(dateFormat)
        if toDate:
            endDate = datetime.datetime(currentDate["year"], 12, 31, 12, 00)
        else:
            endDate = datetime.datetime(newYear, 12, 31, 12, 00)
        endDate = endDate.strftime(dateFormat)
        return [startDate,endDate]

    def mois(self, remove=1,dateFormat="%Y%m%d",toDate=False):
        currentDate = self.getCurrentDate()
        newMonth = currentDate["month"] - remove
        year = currentDate["year"]
        if (newMonth<=0):
            newMonth += 12
            year -= 1
        last_m, last_day = monthrange(year, newMonth)
        startDate = datetime.datetime(year, newMonth, 1, 12, 00)
        startDate = startDate.strftime(dateFormat)
        if toDate:
            endDate = datetime.datetime(currentDate["year"], currentDate["month"], currentDate["day"], 12, 00)
        else:
            endDate = datetime.datetime(year, newMonth, last_day, 12, 00)
        endDate = endDate.strftime(dateFormat)
        return [startDate,endDate]

    def semaine(self, remove=1,dateFormat="%Y%m%d",toDate=False):
        currentDate = self.getCurrentDate()
        newWeek = currentDate["week"] - remove
        year = currentDate["year"]
        if (newWeek<=0):
            newWeek += 52
            year -= 1
        stime = time.strptime('{} {} 1'.format(year, newWeek), '%Y %W %w')
        sDay,sMonth = stime.tm_mday,stime.tm_mon
        etime = time.strptime('{} {} 1'.format(year, newWeek+1), '%Y %W %w')
        eDay,eMonth = etime.tm_mday,etime.tm_mon
        startDate = datetime.datetime(year, sMonth, sDay, 12, 00)
        startDate = startDate.strftime(dateFormat)
        if toDate:
            endDate = datetime.datetime(currentDate["year"], currentDate["month"], currentDate["day"], 12, 00)
        else:
            endDate = datetime.datetime(year, eMonth, eDay, 12, 00)
        endDate = endDate.strftime(dateFormat)
        return [startDate,endDate]

    def jour(self, remove=1,dateFormat="%Y%m%d"):
        currentDate = self.getCurrentDate()
        newDay = currentDate["day"] - remove
        year = currentDate["year"]
        month_to_take = currentDate["month"]
        newMonth = currentDate["month"] - 1
        if (newMonth<=0):
            newMonth += 12
            year -= 1
        last_previous_m, last_previous_day = monthrange(year, newMonth)
        if newDay<=0:
            newDay = last_previous_day
            month_to_take = newMonth
        startDate = datetime.datetime(year, month_to_take, newDay, 12, 00)
        startDate = startDate.strftime(dateFormat)
        endDate = datetime.datetime(year, month_to_take, currentDate["day"], 12, 00)
        endDate = endDate.strftime(dateFormat)
        return [startDate,endDate]

    def extract_numerical(self,sentence,text=False):
        sentence_split = self.clean(sentence)#.split(" ")
        sentence_length = len(sentence_split)
        date_part,date_string = [],"abcdefghijklmnopqrstuvw"
        allDates = []
        order = {
            "day": {
                "words": day_words,
                "function": self.jour
            },"week": {
                "words": week_words,
                "function": self.semaine
            },"month": {
                "words": month_words,
                "function": self.mois
            },"year": {
                "words": year_words,
                "function": self.annee
            },
        }

        for key in order:
            for date_word in order[key]["words"]:
                try:
                    date_word_index = sentence_split.index(date_word)
                    days_diff = int(order[key]["words"][date_word])
                    if days_diff == -1:
                        new_dates_array = order[key]["function"](remove=0,toDate=True)
                        allDates.append(new_dates_array)
                    else:
                        days_diff_amount = int(self.getPreviousAmount(date_word_index, sentence_split))
                        print("{} : {}".format(days_diff,days_diff_amount))
                        total_days = days_diff*days_diff_amount
                        print("Total days "+str(total_days))
                        new_dates_array = order[key]["function"](remove=total_days)
                        allDates.append(new_dates_array)
                        allDates.append(order[key]["function"](remove=total_days+1))
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


datex = DateExtractor()
#print(datex.getPrevious("20160510",7))

print(datex.extract_numerical("ou vend on le plus de bags hier"))
