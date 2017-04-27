# Pour pouvoir importer les fichiers sql
# from importlib.machinery import SourceFileLoader

# foo = SourceFileLoader("sql.request", "../sql/request.py").load_module()
# foo = SourceFileLoader("sql.tables", "../sql/tables.py").load_module()


from sql.request import query

# Import de toutes les tables utilisées
from sql.tables import item, sale, boutique, country, division, retail, theme, department

class Vente(object):

	def __init__(self, data):
		self.cities = data['cities']
		self.countries = data['countries']
		self.nationalities = data['nationalities']
		self.dates = data['dates']
		self.numerical_dates = data['numerical_dates']
		self.items = data['items']
		self.boutiques = data['boutiques']
		self.sentence = data['sentence']

	def build_answer(self):
		response_base = self.build_query()
		print(response_base)
		response_complete = self.append_details(response_base[1])
		return [response_base[0],response_complete] 


	def build_query(self):

		location_query = False
		colour_query = False
		price_query = False

		first_word = self.sentence.split(" ")[0]

		if ('Où' in self.sentence) or ('où' in self.sentence) or ('ou' in first_word) or ('Ou' in first_word) or ('dans quel pays' in self.sentence.lower()) or ('a quel endroit' in self.sentence.lower()):
			print("Sale specific to a location")
			location_query = True

		if ('couleur' in self.sentence.lower()):
			print("Sale specific to a colour")
			colour_query = True

		if ('prix' in self.sentence.lower()):
			print("Sale specific to a price")
			price_query = True

		if len(self.items) == 0:
			return "Veuillez préciser un produit svp"

		product_query = query(sale, ['count(*)'])

		if colour_query:
			product_query = query(sale, ['Color','count(*)'], top_distinct='DISTINCT TOP 5')
		elif location_query:
			product_query = query(sale, [(boutique, 'Description'),'count(*)'], top_distinct='DISTINCT TOP 5')
		elif price_query:
			product_query = query(sale, ['Std_RP_WOTax_REF'], top_distinct='DISTINCT TOP 1')

		# Initialisation de la query : par défaut pour l'instant on sélectionne count(*)

		product_query.join(sale, item, "Style", "Code") # jointure sur ITEM_Code = SALE_Style
		product_query.join(sale, boutique, "Location", "Code") # jointure sur SALE_Location = LOCA_Code

		# S'il n'y a pas de ville, on s'intéresse au pays
		if len(self.countries) > 0:
			product_query.join(sale, country, "Country", "Code") # jointyre sur SALE_Country = COUN_Code

		# Maintenant que toutes les jointures sont faites, on passe aux conditions
		produit_seen = False
		division_seen = False
		department_seen = False
		retail_seen = False
		theme_seen = False

		for produit in self.items :
			for produit_key in produit:
				if produit_key == "division":
					if not produit_seen:
						product_query.join(sale, division,"Division","Code")
						produit_seen = True
				elif produit_key == "departement":
					if not department_seen:
						product_query.join(sale, department,"Department","Code")
						department_seen = True
				elif produit_key == "groupe":
					if not retail_seen:
						product_query.join(sale, retail,"Group","Code")
						retail_seen = True
				elif produit_key == "theme":
					if not theme_seen:
						product_query.join(sale, theme,"Theme","Code")
						theme_seen = True

		for produit in self.items :
			for produit_key in produit:
				if produit_key == "division":
					product_query.where(division, "Description", produit[produit_key])
				elif produit_key == "departement":
					product_query.where(department, "Description", produit[produit_key])
				elif produit_key == "groupe":
					product_query.where(retail, "Description", produit[produit_key])
				elif produit_key == "theme":
					product_query.where(theme, "Description", produit[produit_key])
				elif produit_key == "produit":
					product_query.where(item, "Description", produit[produit_key])

		for ville in self.cities :
			product_query.where(boutique, "Description", ville)

		if len(self.cities) == 0:
			for pays in self.countries :
				product_query.where(country, "Description_FR", pays)

		if len(self.boutiques) > 0:
			for _boutique in self.boutiques :
				product_query.where(boutique, "Description", _boutique)

		if len(self.numerical_dates) > 0:
			product_query.wheredate(sale, 'DateNumYYYYMMDD', self.numerical_dates[0])
		else:
			product_query.wheredate(sale, 'DateNumYYYYMMDD') # par défaut sur les 7 derniers jours

		if colour_query:
			product_query.groupby(sale, 'Color')
			product_query.orderby('count(*)', " DESC")
			query_result = product_query.write().split('\n')
			print(query_result)
			result = [w.split("|")[0]+" ( "+w.split("|")[1]+" vendus )" for w in query_result if 'SALE_Color' not in w and '------' not in w]
			if len(result) > 0:
				if 'le plus' in self.sentence or 'la plus' in self.sentence:
					print("Wanting the top one from: ")
					print(result)
					result_string = "La couleur la plus vendue est "+result[0]+" pour "+",".join(self.items)
					print("retourne: "+result_string)
					if result_string[-1] == ",":
						result_string = result_string[:-1]
					return result_string
				else:
					return [product_query.request,";;".join(result)]
			else:
				return [product_query.request,"Aucune couleur enregistrée pour "+",".join(self.items)]
		elif location_query:
			product_query.groupby(boutique, 'Description')
			product_query.orderby('count(*)', " DESC")
			query_result = product_query.write().split('\n')
			print(query_result)
			result = [w.split("|")[0]+" ( "+w.split("|")[1]+" vendus )" for w in query_result if 'LOCA_Description' not in w and '------' not in w]
			print(result)
			return [product_query.request,";;".join(result)]
		elif price_query:
			query_result = product_query.write().split('\n')
			print(query_result)
			result = [w+"€" for w in query_result if 'SALE_Std_RP_WOTax_REF' not in w and '------' not in w]
			print(result)
			return [product_query.request,";;".join(result)]
		else:			
			# La requête est terminée, on l'écrit
			# product_query.write()
			result = product_query.write().split('\n')
			print("***************")
			return [product_query.request,";;".join(result)]

	def append_details(self, text):
		resp = text[:]+";;"
		if (len(self.cities)>0 or len(self.countries)>0):
			resp += "Avec un critère géographique ("
			if len(self.cities)>0:
				resp += ",".join(self.cities)+","
			if len(self.countries)>0:
				resp += ",".join(self.countries)+","
			if resp[-1]==",":
				resp = resp[:-1]
			resp += ");;"
		if len(self.nationalities)>0:
			resp += "Avec un critère de nationalité ("+",".join(self.nationalities)
			if resp[-1]==",":
				resp = resp[:-1]
			resp += ");;"
		if len(self.dates)>0:
			resp += "Avec un critère de date ("+",".join(self.dates)
			if resp[-1]==",":
				resp = resp[:-1]
			resp += ");;"
		return resp
#
# data = {
# 		'cities' : ['Paris', 'Madrid'],
# 		'countries' : [],
# 		'nationalities' : [],
# 		'dates' : [],
# 		'items' : ['robe']
# 		}
#
# test = Produit(data)
# print(test.build_query())
