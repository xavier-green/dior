# Pour pouvoir importer les fichiers sql
# from importlib.machinery import SourceFileLoader

# foo = SourceFileLoader("sql.request", "../sql/request.py").load_module()
# foo = SourceFileLoader("sql.tables", "../sql/tables.py").load_module()


from sql.request import query

# Import de toutes les tables utilisées
from sql.tables import item, sale, boutique, country

class Produit(object):

	def __init__(self, data):
		self.cities = data['cities']
		self.countries = data['countries']
		self.nationalities = data['nationalities']
		self.dates = data['dates']
		self.items = data['items']

	def build_answer(self):
		response_base = self.build_query()
		print(response_base)
		sock = socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
		sock.connect('/tmp/request.sock')
		sock.sendall(bytes(response_base, 'utf-8'))
		out = sock.recv(8192).decode('utf-8').splitlines()[:-2]
		out.pop(1)
		response_complete = self.append_details(response_base)
		return response_complete + '\n'.join(out)


	def build_query(self):
		# bdd = item_item
		# geo ou date -> vente (sales_sales) / (stock)
		# select COUNT
		# nationalites -> vente
		# item obligatoire

		# IN PROGRESS


		if len(self.items) == 0:
			return "Veuillez préciser un produit svp"

		# Initialisation de la query : par défaut pour l'instant on sélectionne count(*)
		product_query = query(item, ['count(*)'])

		# S'il y a une précision, on considère que ça concerne des ventes
		# On fait les jointures en fonction
		if len(self.cities)+len(self.countries)+len(self.nationalities)+len(self.dates) > 0:
			product_query.join(item, sale, "Code", "Style") # jointure sur ITEM_Code = SALE_Style

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

		# La requête est terminée, on l'écrit
		product_query.write()
		return product_query.request

		# Test de Rémi
		# else:
		# 	demande = query(item, ['Description'], 50)
		# 	for search_item in self.items:
		# 		demande.where(item, 'Description', search_item)
		# 	demande.groupby(item, 'Description')
		# 	return demande.write()

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
