def find_query_type(sentence):

	query_type = {
			"location":False,
			"colour":False,
			"price":False,
			"exceptionnal":False,
			"croissance":False,
			"margin":False,
			"nationality":False,
			"quantity":False,
			"netsale":False,
			"foreign":False
		}

	first_word = self.sentence.split(" ")[0].lower()
	question = self.sentence.lower()

	if ('où' in question) or (first_word == "ou") or ('dans quel pays' in question) or ('a quel endroit' in question):
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
		exceptionnal_query = True

	if ('margin' in question) or ('marge' in question):
		margin_query = True

	if ('croissance' in question) or ('trend' in question):
		print("Sale specific to a croissance")
		croissance_query = True

	if ('local' in question or 'locaux' in question):
		nationality_query = True

	if ('touriste' in question) or ('foreign' in question):
		nationality_query = True
		touriste = True

	if ('net sale' in question) or ('pour combien' in question) or ('valeur' in question):
		netsale_query = True

	if ('quantite' in question) or ('volume' in question) or ('nombre' in question) or ("combien" in question and not "pour combien" in question):
		quantity_query = True

	if (not croissance_query and not exceptionnal_query) and len(self.items) == 0:
		return "Veuillez préciser un produit svp"