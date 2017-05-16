from sql.tables import sale

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