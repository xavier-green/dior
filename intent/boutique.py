from sql.request import query

# Import de toutes les tables utilisées
from sql.tables import item, sale, boutique, country, division, retail, theme, department, zone, sub_zone, uzone

from annexes.mise_en_forme import affichage_euros, affichage_date
from annexes.gestion_geo import geography_joins, geography_select
from annexes.gestion_products import what_products, sale_join_products, query_products, where_products
from annexes.gestion_details import append_details_date, append_details_products, append_details_geo, find_category

class Boutique(object):

	def __init__(self, data):
		self.geo = data['geo']
		# self.nationalities = data['nationalities']
		self.dates = data['dates']
		self.numerical_dates = data['numerical_dates']
		self.items = data['items']
		self.sentence = data['sentence']

	def build_answer(self):
		response_base = self.build_query()
		print(response_base)
		response_complete = response_base[1]

		details_query = response_base[2] if len(response_base) > 2 else "No details"
		return [response_base[0],response_complete, details_query]


	def build_query(self):

		"""
		Creation de la query secondaire pour un join futur
		"""

		sale_table = query(sale, ['*'])

		sale_table.join(sale, zone, 'Zone', 'Code')
		sale_table.whereNotJDAandOTH()

		if len(self.numerical_dates) > 0:
			sale_table.wheredate(sale, 'DateNumYYYYMMDD', self.numerical_dates[0][0], self.numerical_dates[0][1])
		else:
			sale_table.wheredate(sale, 'DateNumYYYYMMDD') # par défaut sur les 7 derniers jours


		"""
		Initialisation et jointure de la vraie query
		"""

		if "zone" in self.sentence.lower():
			boutique_query = query(zone, ['Description', 'count(*)', ("sum", sale, "RG_Net_Amount_WOTax_REF", sale, "MD_Net_Amount_WOTax_REF")], 'TOP 7')
			main_scale = "zone"
			scale_cible = "zones"
			boutique_query.join_custom(zone, sale_table.request, sale, "Code", "Zone")
		elif "pays" in self.sentence.lower():
			boutique_query = query(country, ['Description', 'count(*)', ("sum", sale, "RG_Net_Amount_WOTax_REF", sale, "MD_Net_Amount_WOTax_REF")], 'TOP 3')
			main_scale = "country"
			scale_cible = "pays"
			boutique_query.join_custom(country, sale_table.request, sale, "Code", "Country")
		else:
			boutique_query = query(boutique, ['Description', 'count(*)', ("sum", sale, "RG_Net_Amount_WOTax_REF", sale, "MD_Net_Amount_WOTax_REF")], 'TOP 3')
			main_scale = "boutique"
			scale_cible = "boutiques"
			boutique_query.join_custom(boutique, sale_table.request, sale, "Code", "Location")


		"""
		Jointures
		"""
		
		boutique_query = sale_join_products(boutique_query, self.items)
		boutique_query = geography_joins(boutique_query, self.geo, already_joined = [main_scale])

		"""
		Conditions
		"""

		boutique_query = where_products(boutique_query, self.items)
		boutique_query = geography_select(boutique_query, self.geo)

		"""
		Finitions
		"""

		if scale_cible == 'pays':
			boutique_query.groupby(country, 'Description')
		elif scale_cible == 'zones':
			boutique_query.groupby(zone, 'Description')
		else:
			boutique_query.groupby(boutique, 'Description')

		boutique_query.orderby(None, ("sum", sale, "RG_Net_Amount_WOTax_REF", sale, "MD_Net_Amount_WOTax_REF"), " DESC")


		"""
		Traitement de la réponse
		"""

		# La requête est terminée, on utilise le résultat
		result = boutique_query.write()
		print("***************\n", result)

		reponse = "Voici les " + scale_cible + " ayant eu les meilleures ventes : \n"

		liste_resultat = result.split("\n")
		for n, ligne in enumerate(liste_resultat):
			if n == 0:
				pass
			elif len(ligne.split('#')) == 3:
				colonnes = ligne.split('#')
				nom, nombre_ventes, montant_ventes = colonnes
				reponse += nom + " avec " + nombre_ventes + " ventes pour un montant de " + affichage_euros(montant_ventes) + " HT ; \n"
			else:
				reponse = "Aucun(e) " + scale_cible + " n'a réalisé ce genre de vente durant cette période."

		"""
		Ajout des détails
		"""

		details = append_details_date([], self.numerical_dates)
		details = append_details_products(details, self.items, self.product_sources)
		details = append_details_geo(details, self.geo)

		return [boutique_query.request, reponse, details]

