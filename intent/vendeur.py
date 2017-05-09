from sql.request import query
from intent.mise_en_forme import affichage_euros, affichage_date

# Import de toutes les tables utilisées
from sql.tables import staff, sale, boutique, country, item, zone, division, department, theme, retail

"""
# Pour pouvoir importer les fichiers sql
from importlib.machinery import SourceFileLoader

foo = SourceFileLoader("sql.request", "../sql/request.py").load_module()
foo = SourceFileLoader("sql.tables", "../sql/tables.py").load_module()
"""

class Vendeur(object):

	def __init__(self, data):
		self.cities = data['cities']
		self.countries = data['countries']
		self.nationalities = data['nationalities']
		self.numerical_dates = data['numerical_dates']
		self.dates = data['dates']
		self.items = data['items']
		self.sentence = data['sentence']

	def build_answer(self):
		response_base = self.build_query()
		response_complete = response_base[1]
		return [response_base[0],response_complete]


	def build_query(self):

		"""
		Initialisation de la query
		"""

		seller_query = query(staff, ['Name', 'count(*)', ("sum", sale, "Std_RP_WOTax_REF")], 'TOP 3')


		"""
		Jointures
		"""

		# Jointure particulière avec la table sale ne contenant que les dates intéressantes
		sale_table = query(sale, ['*'])

		# Retirer les éléments de JDA et OTH
		sale_table.join(sale, zone, 'Zone', 'Code')
		sale_table.whereNotJDAandOTH()

		if len(self.numerical_dates) > 0:
			sale_table.wheredate(sale, 'DateNumYYYYMMDD', self.numerical_dates[0])
		else:
			sale_table.wheredate(sale, 'DateNumYYYYMMDD') # par défaut sur les 7 derniers jours

		seller_query.join_custom(staff, sale_table.request, sale, "Code", "Staff") # jointure sur STAFF_Code = SALE_Staff

		# S'il y a une ville, on fait JOIN sur la table des boutiques
			# On n'a pas moyen de savoir où travaille un vendeur donc on cherche dans SALE
		if len(self.cities) > 0:
			seller_query.join(sale, boutique, "Location", "Code") # jointure sur SALE_Location = LOCA_Code

		elif len(self.countries) > 0:
			seller_query.join(sale, country, "Country", "Code") # jointure sur SALE_Country = COUN_Code

		categorie_produit = ''
		produit_selected = []
		for produit in self.items :
			for produit_key in produit:
				if produit_key == "division":
					seller_query.join(sale, division,"Division","Code")
					categorie_produit = "la division "
					produit_selected.append(produit[produit_key])
				elif produit_key == "departement":
					seller_query.join(sale, department,"Department","Code")
					categorie_produit = "le departement "
					produit_selected.append(produit[produit_key])
				elif produit_key == "groupe":
					seller_query.join(sale, retail,"Group","Code")
					categorie_produit = "le groupe retail "
					produit_selected.append(produit[produit_key])
				elif produit_key == "theme":
					seller_query.join(sale, theme,"Theme","Code")
					categorie_produit = "le theme "
					produit_selected.append(produit[produit_key])
				elif produit_key == "produit":
					seller_query.join(sale, item,"Style","Code")
					categorie_produit = "le produit "
					produit_selected.append(produit[produit_key])

		"""
		Conditions
		"""

		for produit in self.items :
			for produit_key in produit:
				if produit_key == "division":
					seller_query.where(division, "Description", produit[produit_key])
				elif produit_key == "departement":
					seller_query.where(department, "Description", produit[produit_key])
				elif produit_key == "groupe":
					seller_query.where(retail, "Description", produit[produit_key])
				elif produit_key == "theme":
					seller_query.where(theme, "Description", produit[produit_key])
				elif produit_key == "produit":
					seller_query.where(item, "Description", produit[produit_key])

		for ville in self.cities :
			seller_query.where(boutique, "Description", ville)

		if len(self.cities) == 0:
			for pays in self.countries :
				seller_query.where(country, "Description_FR", pays)

		"""
		Finitions
		"""

		# On n'oublie pas le GROUP BY, nécessaire ici vu qu'on prend à la fois une colonne et un count(*)
		seller_query.groupby(staff, 'Name')
		seller_query.orderby(None, ('sum', sale, 'Std_RP_WOTax_REF'), " DESC")

		"""
		Traitement du résultat
		"""

		result = seller_query.write()
		print("***************")
		print(result)
		reponse = "Voici les 3 meilleurs vendeurs "
		start_date = affichage_date(self.numerical_dates[0]) if len(self.numerical_dates) > 0 else affichage_date('20170225')
		reponse += "du " + start_date + " au " + affichage_date("20170304") + " "
		reponse += "pour " + categorie_produit + ', '.join(produit_selected) + " " if len(produit_selected) > 0 else ''
		reponse += "de la boutique de " + ', '.join([b for b in self.cities]) + " " if len(self.cities) > 0 else ''
		reponse += "dans le pays " + ", ".join([p for p in self.countries]) + " " if len(self.cities) == 0 and len(self.countries) > 0 else ''
		reponse += " : \n"

		liste_resultat = result.split("\n")
		for n, ligne in enumerate(liste_resultat):
			if n == 0:
				pass
			else:
				nom_vendeur, nombre_ventes, montant_ventes = ligne.split('|')
				reponse += nom_vendeur + " avec " + nombre_ventes + " ventes pour un montant de " + affichage_euros(montant_ventes) + " HT ; \n"

		return [seller_query.request,reponse]

"""
data = {
		'cities': [],
		'countries': [],
		'nationalities': [],
		'numerical_dates': [],
		'dates': [],
		'items': {},
		'sentence': []
		}

test = Vendeur(data)
print(test.build_answer())"""
