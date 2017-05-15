"""
Dans ce glossaire, les mots de gauche seront remplacés
par les mots de droite lors de la lecture de la question
ex : ventes de PAP femme > ventes de ready to wear women
"""

from data.glossaire import glossaire_1G, glossaire_2G, glossaire_3G, glossaire_4G
from nltk.util import ngrams

def glossaire_NG(text, glossaire, n):
    text_words = text.split(" ")
    text_ngrams = ngrams(text_words, n)
    for i, ngram in enumerate(text_ngrams):
        glossaire_key = " ".join(ngram)
        if glossaire_key in glossaire:
            print("On remplace", text_words[i], "par", glossaire[glossaire_key])
            text_words[i] = glossaire[glossaire_key]
            for j in range(1,n):
                text_words[i+j] = ""
    return " ".join(text_words)

def translate_with_glossaire(text):
    print("Question initiale :", text)
    response = glossaire_NG(text, glossaire_4G, 4)
    response = glossaire_NG(response, glossaire_3G, 3)
    response = glossaire_NG(response, glossaire_2G, 2)
    response = glossaire_NG(response, glossaire_1G, 1)
    print("Question finale :\n", response)
    return response
