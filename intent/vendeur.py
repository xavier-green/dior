from sql.request import query

# Import de toutes les tables utilisées
from sql.tables import staff, sale, boutique, country, item

class Vendeur(object):

	def __init__(self, data):
		self.cities = data['cities']
		self.countries = data['countries']
		self.nationalities = data['nationalities']
		self.numerical_dates = data['numerical_dates']
		self.dates = data['dates']
		self.items = data['items']
	
	def build_answer(self):
		response_base = self.build_query()
		response_complete = self.append_details(response_base)
		return response_complete
	
	
	def build_query(self):
		# bdd = item_item
		# geo ou date ou item -> vente (sales_sales) / location
		# On le mettra par défaut
		# select NAME par défaut
		# obligatoirement : rien, par défaut on sélectionne les 10 meilleurs vendeurs au monde
		# et on affiche leur nombre de ventes

		# IN PROGRESS

		# Initialisation de la query : par défaut pour l'instant on sélectionne le nom
		seller_query = query(staff, ['Name', 'count(*)'], 10)
		
		# Par défaut, on joint les sales parce que ça nous intéresse
		# Mais attention il faut joindre avec un set de date parce que sinon la reuqête timeout
		sale_table = query(sale, ['*'])
		
		if len(self.numerical_dates) > 0:
			sale_table.wheredate(sale, 'DateNumYYYYMMDD', self.numerical_dates[0])
		else:
			sale_table.wheredate(sale, 'DateNumYYYYMMDD') # par défaut sur les 7 derniers jours
		
		seller_query.join_custom(staff, sale_table.request, sale, "Code", "Staff") # jointure sur STAFF_Code = SALE_Staff
		
		# S'il y a une ville, on fait JOIN sur la table des boutiques
			# On n'a pas moyen de savoir où travaille un vendeur donc on cherche dans SALE
		if len(self.cities) > 0:
			seller_query.join(sale, boutique, "Location", "Code") # jointure sur SALE_Location = LOCA_Code
		
		# S'il n'y a pas de ville, on s'intéresse au pays
		elif len(self.countries) > 0:
			seller_query.join(sale, country, "Country", "Code") # jointure sur SALE_Country = COUN_Code
		
		# S'il y a un produit, on join avec item aussi
		if len(self.items) > 0:
			seller_query.join(sale, item, "Style", "Code") # jointure sur SALE_Style = ITEM_Code
		
		# Maintenant que toutes les jointures sont faites, on passe aux conditions
		for produit in self.items :
			seller_query.where(item, "Description", produit)
		
		for ville in self.cities :
			seller_query.where(boutique, "Description", ville)
			
		if len(self.cities) == 0:
			for pays in self.countries :
				seller_query.where(country, "Description_FR", pays)
		
		# On n'oublie pas le GROUP BY, nécessaire ici vu qu'on prend à la fois une colonne et un count(*)
		seller_query.groupby(staff, 'Name')
		seller_query.orderby('count(*)', " DESC")
		
		# La requête est terminée, on l'écrit
		result = seller_query.write()
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


# Pour tester
data = {
		'cities' : ['Montaigne'],
		'countries' : [],
		'nationalities' : [],
		'dates' : [],
		'numerical_dates' : ['20170226'],
		'items' : []
		}

# test = Vendeur(data)
# print(test.build_query())