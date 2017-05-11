"""
Dans ce glossaire, les mots de gauche seront remplacés
par les mots de droite lors de la lecture de la question
"""

glossaire_1G = {
    "femme":"women",
    "femmes":"women",
    "woman":"women",
    "homme":"men",
    "hommes":"men",
    "man":"men",
    "maro" : "leather",
    "maroquinerie":"leather",
    "accessoire":"accessories",
    "accessoires":"accessories",
    "joa":"jewellery",
    "jo":"jewellery",
    "joaillerie":"jewellery",
    "horlo":"watches",
    "CJ":"custom jewellery",
    "parapluie":"umbrellas",
    "parapluies":"umbrellas",
    "lunette":"eyewear",
    "lunettes":"eyewear",
    "sunglasses":"eyewear",
    "chapeau":"hats",
    "chapeaux":"hats",
    "echarpe":"scarves",
    "echarpes":"scarves",
    "fourrure":"fur",
    "fourrures":"fur",
    "chemise":"shirts",
    "chemises":"shirts",
    "cravatte":"ties",
    "cravattes":"ties",
    "sac":"bags",
    "sacs":"bags",
    "ceinture":"belts",
    "ceintures":"belts",
    "soulier":"shoes",
    "souliers":"shoes",
    "haute":"high",
    "moyenne":"middle",
    "petite":"little",
    "bracelet":"straps",
    "bracelets":"straps",
    "stylo":"pens",
    "stylos":"pens",
    "objet":"objects",
    "objets":"objects",
    "mobilier":"furniture",
    "mobiliers":"furniture"
}

glossaire_2G = {
    "time pieces":"watches",
    "demi mesure":"Mesure-1/2 mesure",
    "petite maro":"SLG",
    "fashion jo":"custom jewellery",
    "fashion joaillerie":"custom jewellery",
    "haute horlo":"high horology",
    "haute horlogerie":"high horology",
    "horlo precieuse":"precious timepieces",
    "horlogerie precieuse":"precious timepieces",
}

glossaire_3G = {
    "linge de maison":"home linens",
    "small leather goods":"SLG"
}

glossaire_4G = {
    "art de la table":"gift tableware"
}

"""
Fonctions du glossaire
"""

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
