"""
Ce glossaire est un dictionnaire où le mot de gauche sera remplacé par le mot de droite.
ex : "femme" sera traduit en "women"
Il y a quatre glossaires suivant le nombre de mots à traduire
ex : "art de la table" fait quatre mots, il est dans le glossaire 4G
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
    "horlogerie":"watches",
    "cj":"custom jewellery",
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
    "cravate":"ties",
    "cravates":"ties",
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
    "mobiliers":"furniture",
    "pap":"ready to wear",
}

glossaire_2G = {
    "time pieces":"watches",
    "demi mesure":"mesure-1/2 mesure",
    "petite maro":"slg",
    "fashion jo":"custom jewellery",
    "fashion joaillerie":"custom jewellery",
    "haute horlo":"high horology",
    "haute horlogerie":"high horology",
    "horlo precieuse":"precious timepieces",
    "horlogerie precieuse":"precious timepieces",
    "lunettes femme":"women eyewear",
    "lunettes homme":"men eyewear",
    "souliers femme":"women shoes"
}

glossaire_3G = {
    "linge de maison":"home linens",
    "small leather goods":"slg",
    "pret a porter": "ready to wear"
}

glossaire_4G = {
    "art de la table":"gift tableware"
}

"""
Le code ci-dessous permet d'importer les dictionnaires précédents au format XLS
"""
"""
import xlwt

book = xlwt.Workbook(encoding="utf-8")
sheet = book.add_sheet("Sheet 1")
sheet.write(0,0, "mot")
sheet.write(0,1, "traduction")
i = 1
for dictionnaire in [glossaire_1G, glossaire_2G, glossaire_3G, glossaire_4G]:
        for key in dictionnaire:
            sheet.write(i, 0, key)
            sheet.write(i, 1, dictionnaire[key])
            i += 1
book.save("glossaire.xls")
"""