from sql.tables import sale
from annexes.mise_en_forme import affichage_euros, separateur_milliers
from annexes.gestion_details import find_category

def find_query_type(sentence):
	"""
	Permet à partir d'une phrase, d'en extraire un intent plus précis
	ex : "Où vend-on le plus aux touristes ?" > location, nationality, foreign
	ex : "Quelle est la croissance de Lady Dior ?" > croissance
	"""

	query_type = {
			"location":False,
			"colour":False,
			"price":False,
			"exceptionnal":False,
			"croissance":False,
			"margin":False,
			"nationality":False,
			"foreign":False,
			"netsale":False,
			"quantity":False
		}

	question = sentence.lower()
	question_words = question.split(" ")
	first_word = question_words[0]

	if ('où' in question_words) or (first_word == "ou") or ('dans quel pays' in question) or ('a quel endroit' in question):
		print("Sale specific to a location")
		query_type["location"] = True

	if ('couleur' in question):
		print("Sale specific to a colour")
		query_type["colour"] = True

	if ('prix' in question):
		print("Sale specific to a price")
		query_type["price"] = True

	if ('exceptionnel' in question):
		print("Sale specific to exceptionnal sales")
		query_type["exceptionnal"] = True

	if ('croissance' in question) or ('trend' in question):
		print("Sale specific to a croissance")
		query_type["croissance"] = True

	if ('margin' in question) or ('marge' in question):
		query_type["margin"] = True

	if ('local' in question or 'locaux' in question):
		query_type["nationality"] = True

	if ('touriste' in question) or ('foreign' in question):
		query_type["nationality"] = True
		query_type["foreign"] = True

	if ('net sale' in question) or ('pour combien' in question) or ('valeur' in question):
		query_type["netsale"] = True

	if ('quantite' in question) or ('volume' in question) or ('nombre' in question) or ("combien" in question and not "pour combien" in question):
		query_type["quantity"] = True

	return query_type

def find_MDorFP(sentence):
	"""
	Trouve si la question porte sur un Mark Down ou un Full Price, et indique les colonnes à sélectionner en fonction
	"""

	question = sentence.lower().split(" ")
	Quantity_requested = []
	if 'fp' in question or ('full' in question and 'price' in question):
		Quantity_requested.append('fp')
	if 'md' in question or ('mark' in question and 'down' in question):
		Quantity_requested.append('md')

	if len(Quantity_requested) == 0 or len(Quantity_requested) == 2:
		Quantity = ('sum', sale, 'RG_Quantity', sale, 'MD_Quantity')
		MDorFP = ""
	elif Quantity_requested[0] == 'fp':
		Quantity = ('sum', sale, 'RG_Quantity')
		MDorFP = "en Full Price "
	else:
		Quantity = ('sum', sale, 'MD_Quantity')
		MDorFP = "en Mark Down "

	return MDorFP, Quantity

def calcul_somme_ventes(query_result, details, quantity = False, value = False):
	"""
	A partir d'une query_result comportant à la fin [nom, nb_vente (if quantity), prix_vente (if value)],
	renvoit la quantite de ventes totale et le CA total,
	tout en ajoutant le détail aux détails.
	"""
	assert (quantity or value), "Vous n'avez demandé ni quantité ni valeur"
	
	valeur = 0
	quantite = 0
	for n, ligne in enumerate(query_result):
		if len(ligne.split('#')) < 2:
			print("result was null")
			return details, quantite, valeur
		if n == 0:
			colonnes = ligne.split('#')
			categorie = find_category(colonnes[-3]) if value and quantite else find_category(colonnes[-2])
		if n > 0:
			colonnes = ligne.split('#')
			prix_ventes = colonnes[-1] if value else "0"
			quantite_ventes = colonnes[-2] if value else colonnes[-1]
			valeur += float(prix_ventes)
			quantite += int(quantite_ventes)
		if n > 0 and n < 10:
			details_quantity = separateur_milliers(quantite_ventes) + " ventes" if quantity else ""
			details_and = " pour " if quantity and value else ""
			details_value = affichage_euros(prix_ventes) + " HT" if value else ""

			categorie_item = colonnes[-3] if value and quantite else colonnes[-2]

			details.append([categorie + ' ' + categorie_item, details_quantity + details_and + details_value])
		if n == 10:
			details.append(["...", "..."])

	return details, quantite, valeur



