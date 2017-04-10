# coding=utf-8

print("Importing intent class")
from intent import intentModel

print("Importing training data")
from data import intent_data
data = intent_data.intentData.data

print("Importing fasttext model")
import sys
sys.path.append('/usr/local/Cellar/python3/3.6.0/Frameworks/Python.framework/Versions/3.6/lib/python3.6/site-packages')
import fasttext
model_fasttext = fasttext.load_model('/Users/xav/Downloads/wiki.fr/wiki.fr.bin')

print("Training model")

intent_model = intentModel(model_fasttext)
intent_model.train(data, save_file=True)
print(intent_model.predict("Qui est le meilleur vendeur du mois en Chine ?"))