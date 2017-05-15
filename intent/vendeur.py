from sql.request import query
from intent.mise_en_forme import affichage_euros, affichage_date

# Import de toutes les tables utilisées
from sql.tables import staff, sale, boutique, country, item, zone, division, department, theme, retail, zone, uzone, sub_zone

from intent.fonctions_annexes import geography_joins, geography_select
from intent.fonctions_annexes import what_products, sale_join_products, query_products, where_products, find_category
from intent.fonctions_annexes import append_details_date, append_details_products, append_details_geo

class Vendeur(object):

	def __init__(self, data):
		self.geo = data['geo']
		# self.nationalities = data['nationalities']
		self.numerical_dates = data['numerical_dates']
		self.dates = data['dates']
		self.items = data['items']
		self.sentence = data['sentence']
		self.boutiques = data['boutiques']

	def build_answer(self):
		response_base = self.build_query()
		response_complete = response_base[1]
		details_query = response_base[2] if len(response_base) > 2 else "No details"
		return [response_base[0],response_complete, details_query]


	def build_query(self):

		"""
		Query annexe de sale
		"""

		sale_table = query(sale, ['*'])

		sale_table.join(sale, zone, 'Zone', 'Code')
		sale_table.whereNotJDAandOTH()

		if len(self.numerical_dates) > 0:
			sale_table.wheredate(sale, 'DateNumYYYYMMDD', self.numerical_dates[0][0], self.numerical_dates[0][1])
		else:
			sale_table.wheredate(sale, 'DateNumYYYYMMDD') # par défaut sur les 7 derniers jours

		"""
		Initialisation de la query
		"""

		seller_query = query(staff, ['Name', 'count(*)', ("sum", sale, "RG_Net_Amount_WOTax_REF", sale, "MD_Net_Amount_WOTax_REF")], 'TOP 3')


		"""
		Jointures
		"""

		seller_query.join_custom(staff, sale_table.request, sale, "Code", "Staff") # jointure sur STAFF_Code = SALE_Staff

		seller_query = sale_join_products(seller_query, self.items)
		seller_query = geography_joins(sale, seller_query, self.geo)


		"""
		Conditions
		"""

		seller_query = where_products(seller_query, self.items)
		seller_query = geography_select(seller_query, self.geo)


		"""
		Finitions
		"""

		seller_query.groupby(staff, 'Name')
		seller_query.orderby(None, ("sum", sale, "RG_Net_Amount_WOTax_REF", sale, "MD_Net_Amount_WOTax_REF"), " DESC")


		"""
		Traitement du résultat
		"""

		result = seller_query.write()
		print("***************\n", result)

		reponse = "Voici les 3 meilleurs vendeurs : \n"

		liste_resultat = result.split("\n")
		for n, ligne in enumerate(liste_resultat):
			if n == 0:
				pass
			elif len(ligne.split('#')) < 3:
				reponse = "Aucun vendeur n'a réalisé ce genre de vente durant cette période."
			else:
				nom_vendeur, nombre_ventes, montant_ventes = ligne.split('#')
				reponse += nom_vendeur + " avec " + nombre_ventes + " ventes pour un montant de " + affichage_euros(montant_ventes) + " HT ; \n"

		"""
		Ajout des details
		"""

		details = append_details_date([], self.numerical_dates)
		details = append_details_products(details, self.items)
		details = append_details_geo(details, self.geo)

		return [seller_query.request, reponse, details]
