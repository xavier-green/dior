from copy import copy

from sql.request import query

from annexes.mise_en_forme import affichage_euros, affichage_date, separateur_milliers
from annexes.gestion_dates import last_week, same_week_last_year
from annexes.gestion_geo import geography_joins, geography_select
from annexes.gestion_products import what_products, sale_join_products, query_products, where_products
from annexes.gestion_details import append_details_date, append_details_products, append_details_geo, append_details_boutiques, find_category
from annexes.gestion_intent_vente import find_query_type, find_MDorFP, calcul_somme_ventes

# Import de toutes les tables utilisées
from sql.tables import item, sale, boutique, country, division, retail, theme, department, zone, uzone, sub_zone, color

import math


class Vente(object):

	def __init__(self, data):
		self.geo = data['geo']
		# self.nationalities = data['nationalities']
		self.dates = data['dates']
		self.numerical_dates = data['numerical_dates']
		self.items = data['items']
		self.boutiques = data['boutiques']
		self.sentence = data['sentence']
		self.seuil_exc = data['seuil']
		self.product_sources = data['sources']

	def build_answer(self):
		response_base = self.build_query()
		print(response_base)
		response_complete = response_base[1]
		details_query = response_base[2] if len(response_base) > 2 else "No details"
		return [response_base[0],response_complete, details_query]


	def build_query(self):

		"""
		On cherche quel type de question a été posée
		"""

		query_type = find_query_type(self.sentence)

		if query_type["exceptionnal"] and not self.seuil_exc:
			print("Aucun seuil trouvé, seuil par défault à 50k")
			self.seuil_exc = 50000

		if query_type["margin"] and len(self.items) == 0:
			return [None, "Vous avez posé une question concernant un margin, mais sans préciser le produit associé."]

		elif query_type["price"] and len(self.items) == 0:
			return [None, "Vous avez demandé un prix sans préciser le produit associé."]

		text_MDorFP, quantity_MDorFP = find_MDorFP(self.sentence)

		columns_requested = query_products(self.items)
		column_groupby = columns_requested[:]
		columns_requested.append(quantity_MDorFP)

		"""
		Création de la sous-requêtes pour la table vente
		"""

		sale_table = query(sale, ['*'])

		sale_table.join(sale, zone, 'Zone', 'Code')
		sale_table.whereNotJDAandOTH()

		if len(self.numerical_dates) > 0 and not query_type["croissance"]:
			sale_table.wheredate(sale, 'DateNumYYYYMMDD', self.numerical_dates[0][0], self.numerical_dates[0][1])
		elif query_type["croissance"]:
			pass
		else:
			sale_table.wheredate(sale, 'DateNumYYYYMMDD') # par défaut sur les 7 derniers jours


		"""
		On créé la query en fonction de la question
		"""

		if query_type["colour"]:
			product_query = query(item, [(color, 'Description'), quantity_MDorFP], top_distinct='DISTINCT TOP 3')
		elif query_type["location"]:
			product_query = query(item, [(boutique, 'Description'), quantity_MDorFP], top_distinct='DISTINCT TOP 5')
		elif query_type["price"]:
			product_query = query(item, [(item, "Description"), ("sum", sale, "RG_Net_Amount_WOTax_REF", sale, "MD_Net_Amount_WOTax_REF")], top_distinct='DISTINCT TOP 1')
		elif query_type["exceptionnal"]:
			product_query = query(item, [(item, "Description"), ("sum", sale, "RG_Net_Amount_WOTax_REF", sale, "MD_Net_Amount_WOTax_REF"), "DateNumYYYYMMDD", (boutique, "Description")])
		elif query_type["croissance"]:
			product_query = query(item, [("sum", sale, "RG_Net_Amount_WOTax_REF", sale, "MD_Net_Amount_WOTax_REF")])
		elif query_type["margin"]:
			product_query = query(item, columns_requested + [("sum", sale, "RG_Net_Amount_WOTax_REF", sale, "MD_Net_Amount_WOTax_REF"),("sum", sale, 'Unit_Avg_Cost_REF')])
		else:
			product_query = query(item, columns_requested + [("sum", sale, "RG_Net_Amount_WOTax_REF", sale, "MD_Net_Amount_WOTax_REF")])

		product_query.join_custom(item, sale_table.request, sale, "Code", "Style")

		"""
		Jointures
		"""

		already_joined_geo = []
		if len(self.boutiques) > 0 or query_type["exceptionnal"] or query_type["croissance"] or query_type["location"]:
			product_query.join(sale, boutique, "Location", "Code")
			already_joined_geo.append("boutique")

		if query_type["nationality"]:
			product_query.join(sale, country, "Cust_Nationality", "Code_ISO")
			already_joined_geo.append("country")

		already_joined_product = ["Style"]
		if query_type["colour"]:
			product_query.join(sale, color, "Color", "Code")
			already_joined_product.append("Color")

		product_query = geography_joins(product_query, self.geo, already_joined = already_joined_geo)
		product_query = sale_join_products(product_query, self.items, already_joined = already_joined_product)

		"""
		Conditions
		"""

		if query_type["nationality"]:
			if query_type["foreign"]:
				product_query.whereComparaison(sale, "Country", "<>", "CO.COUN_Code")
			else:
				product_query.whereComparaison(sale, "Country", "=", "CO.COUN_Code")

		product_query = geography_select(product_query, self.geo)
		product_query = where_products(product_query, self.items)

		if len(self.boutiques) > 0:
			for _boutique in self.boutiques :
				product_query.where(boutique, "Description", _boutique)

		"""
		Finitions
		"""

		if query_type["colour"]:
			product_query.groupby(color, 'Description')
			product_query.orderby(None, quantity_MDorFP, " DESC")

		elif query_type["location"]:
			product_query.groupby(boutique, 'Description')
			product_query.orderby(None, quantity_MDorFP, " DESC")

		elif query_type["exceptionnal"]:
			product_query.groupby(item, "Description")
			product_query.groupby(boutique, "Description")
			product_query.groupby(sale, "DateNumYYYYMMDD")
			product_query.having(sale, ("sum", sale, "RG_Net_Amount_WOTax_REF", sale, "MD_Net_Amount_WOTax_REF"), ">", str(self.seuil_exc))

			product_query.orderby(None, ("sum", sale, "RG_Net_Amount_WOTax_REF", sale, "MD_Net_Amount_WOTax_REF"), "DESC")
		
		elif query_type["price"]:
			product_query.groupby(item, "Description")

		elif query_type["croissance"]:
			pass
		
		else:
			for col in column_groupby:
				product_query.groupby(col[0], col[1])

		"""
		Ecriture de la query
		"""

		if not query_type["croissance"]:
			query_result = product_query.write().split('\n')

		"""
		Ecriture des détails
		"""

		if query_type["croissance"]:

			first_start_date, first_end_date = last_week()
			second_start_date, second_end_date = same_week_last_year()

			details = append_details_date([], [[first_start_date, first_end_date]])
			details = append_details_date(details, [[second_start_date, second_end_date]])
			details = append_details_products(details, self.items, self.product_sources)
			details = append_details_geo(details, self.geo)

		else:

			details = append_details_date([], self.numerical_dates)
			details = append_details_products(details, self.items, self.product_sources)
			details = append_details_geo(details, self.geo)

		"""
		Mise en forme de la réponse
		"""

		if query_type["colour"]:
			result = "Voici les couleurs les plus vendues : "
			for n, ligne in enumerate(query_result):
				if n > 0:
					colonnes = ligne.split('#')
					if len(colonnes) != 2:
						result = "\nAucune vente avec des couleurs pour les mots-clés demandés."
					else:
						couleur, nb_ventes = colonnes
						result += "\n" + couleur.rstrip() + " avec " + separateur_milliers(nb_ventes) + " ventes"

		elif query_type["location"]:
			result = "Voici les boutiques avec les meilleurs ventes :"
			for n, ligne in enumerate(query_result):
				if n > 0:
					colonnes = ligne.split('#')
					if len(colonnes) != 2:
						result = "\nAucune vente pour les mots-clés demandés."
					else:
						_boutique, nb_ventes = colonnes
						result += "\n" + _boutique + " avec " + separateur_milliers(nb_ventes) + " ventes"

		elif query_type["price"]:
			if len(query_result) > 1 and len(query_result[1].split('#')) == 2:
				product_name, product_price = query_result[1].split('#')
				result = "Mon premier résultat est " + product_name.rstrip() + " qui s'est vendu à " + affichage_euros(product_price)
			else:
				result = "Aucune vente concernant ces mots-clés, impossible de trouver un prix."

		elif query_type["exceptionnal"]:
			result = "Il y a eu %i ventes exceptionnelles (supérieures à %s)" %(len(query_result)-1, affichage_euros(self.seuil_exc))
			result += "\nVoici les meilleures :" if len(query_result)-1 > 3 else ""

			for n, ligne in enumerate(query_result):
				if n > 0 and n < 4:
					colonnes = ligne.split('#')
					if len(colonnes) == 4:
						item_desc, item_prix, item_date, item_lieu = colonnes
						result += "\n%s vendu pour %s le %s à %s" % (item_desc.rstrip(), affichage_euros(item_prix), affichage_date(item_date), item_lieu)
					else:
						result = "\nAucune vente exceptionnelle pour ces mots-clés"

		elif query_type["margin"]:
			
			margins = []
			total_ventes = 0
			for n, ligne in enumerate(query_result):
				if n > 0:
					colonnes = ligne.split('#')
					if len(colonnes) > 3:
						avg_cost = float(colonnes[-1])
						prix_vente = float(colonnes[-2])
						nb_vente = int(colonnes[-3])
						nom_item = colonnes[-4]
						assert prix_vente != 0, "Prix de vente nul, impossible de calculer le margin"
						margin = (prix_vente-avg_cost)/prix_vente
						margins.append({
							'margin': margin,
							'count': nb_vente
						})
						total_ventes += nb_vente

			margin_global = 0
			for margin in margins:
				margin_global += margin['margin']*margin['count']/total_ventes

			result = "Le margin est de %.2f%%" %(margin_global*100) if len(margins) != 0 else "Impossible de calculer le margin pour les mots-clés donnés, il n'y a pas eu de telles ventes sur cette période."

		elif query_type["croissance"]:
			second_query = copy(product_query)

			product_query.wheredate(sale, 'DateNumYYYYMMDD', first_start_date, first_end_date)
			second_query.wheredate(sale, 'DateNumYYYYMMDD', second_start_date, second_end_date)

			ventes_n = product_query.write().split('\n')
			ventes_n_moins_un = second_query.write().split('\n')
			vente_date_n = ventes_n[1]
			vente_date_n_moins_un = ventes_n_moins_un[1]

			if vente_date_n_moins_un == "NULL" :
				result = "Aucune vente enregistrée l'année dernière pour ces mots-clés"
			elif vente_date_n == "NULL":
				result = "Aucune vente enregistrée la semaine dernière pour ces mots-clés"
			else:
				vente_date_n = float(vente_date_n)
				vente_date_n_moins_un = float(vente_date_n_moins_un)
				croissance = 100 * (vente_date_n - vente_date_n_moins_un) / vente_date_n_moins_un if vente_date_n_moins_un > 0 else 0
				result = "La croissance est de %.2f%% par rapport à l'année dernière" %(croissance)

		elif query_type["quantity"]:
			details, quantite, valeur = calcul_somme_ventes(query_result, details, quantity = True)
			result = "Il y a eu " + separateur_milliers(str(quantite)) + " ventes "
			result += text_MDorFP

		elif query_type["netsale"]:
			details, quantite, valeur = calcul_somme_ventes(query_result, details, value = True)
			result = "Il y a eu " + affichage_euros(str(valeur)) + " HT de CA "
			result += text_MDorFP

		else:
			details, quantite, valeur = calcul_somme_ventes(query_result, details, quantity = True, value = True)
			result = "Il y a eu " + separateur_milliers(str(quantite)) + " ventes pour un total de " + affichage_euros(str(valeur)) + " HT "
			result += text_MDorFP

		"""
		Return
		"""

		print("***************\n" + result + "\n***************")
		print("details :", details)
		return [product_query.request, result, details]


