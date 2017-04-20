# Pour pouvoir importer les fichiers sql
# from importlib.machinery import SourceFileLoader

# foo = SourceFileLoader("sql.request", "../sql/request.py").load_module()
# foo = SourceFileLoader("sql.tables", "../sql/tables.py").load_module()


from sql.request import query

# Import de toutes les tables utilisées
from sql.tables import item, sale, boutique, country

class Vente(object):

	def __init__(self, data):
		self.cities = data['cities']
		self.countries = data['countries']
		self.nationalities = data['nationalities']
		self.dates = data['dates']
		self.numerical_dates = data['numerical_dates']
		self.items = data['items']

	def build_answer(self):
		response_base = self.build_query()
		print(response_base)
		response_complete = self.append_details(response_base)
		return response_complete 


	def build_query(self):

		if len(self.items) == 0:
			return "Veuillez préciser un produit svp"

		# Initialisation de la query : par défaut pour l'instant on sélectionne count(*)
		product_query = query(sale, ['count(*)'])

		# S'il y a une précision, on considère que ça concerne des ventes
		# On fait les jointures en fonction
		if len(self.cities)+len(self.countries)+len(self.nationalities)+len(self.dates) > 0:
			product_query.join(sale, item, "Style", "Code") # jointure sur ITEM_Code = SALE_Style

			# S'il y a une ville, on fait JOIN sur la table des boutiques
			if len(self.cities) > 0:
				product_query.join(sale, boutique, "Location", "Code") # jointure sur SALE_Location = LOCA_Code

			# S'il n'y a pas de ville, on s'intéresse au pays
			elif len(self.countries) > 0:
				product_query.join(sale, country, "Country", "Code") # jointyre sur SALE_Country = COUN_Code

		# Maintenant que toutes les jointures sont faites, on passe aux conditions
		for produit in self.items :
			product_query.where(item, "Description", produit)

		for ville in self.cities :
			product_query.where(boutique, "Description", ville)

		if len(self.cities) == 0:
			for pays in self.countries :
				product_query.where(country, "Description_FR", pays)

		if len(self.numerical_dates)>0:
			product_query.wheredate(sale, 'DateNumYYYYMMDD', self.numerical_dates[0])
			
		print(product_query.request)
		# La requête est terminée, on l'écrit
		# product_query.write()
		result = product_query.write()
		print("***************")
		print(result)
		return result

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
