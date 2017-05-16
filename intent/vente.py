"""
from importlib.machinery import SourceFileLoader

foo = SourceFileLoader("sql.request", "../sql/request.py").load_module()
foo = SourceFileLoader("sql.tables", "../sql/tables.py").load_module()

"""
from copy import copy

from sql.request import query

from annexes.mise_en_forme import affichage_euros, affichage_date
from annexes.gestion_geo import geography_joins, geography_select
from annexes.gestion_products import what_products, sale_join_products, query_products, where_products
from annexes.gestion_details import append_details_date, append_details_products, append_details_geo, append_details_boutiques, find_category
from annexes.gestion_intent_vente import find_query_type, find_MDorFP

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

		first_word = self.sentence.split(" ")[0]
		question = self.sentence.lower()

		if query_type["exceptionnal"] and not self.seuil_exc:
			print("Aucun seuil trouvé, seuil par défault à 10k")
			self.seuil_exc = 10000

		if (not query_type["croissance"] and not query_type["exceptionnal"]) and len(self.items) == 0:
			return "Veuillez préciser un produit svp"

		text_MDorFP, quantity_MDorFP = find_MDorFP(self.sentence)

		columns_requested = query_products(self.items)
		column_groupby = columns_requested[:]
		columns_requested.append(quantity_MDorFP)

		"""
		On créé la query en fonction de la question
		"""

		if query_type["colour"]:
			product_query = query(sale, [(color, 'Description'), 'count(*)'], top_distinct='DISTINCT TOP 5')
		elif query_type["location"]:
			product_query = query(sale, [(boutique, 'Description'), 'count(*)'], top_distinct='DISTINCT TOP 5')
		elif query_type["price"]:
			product_query = query(sale, [(sale, "RG_Net_Amount_WOTax_REF")], top_distinct='DISTINCT TOP 1')
		elif query_type["exceptionnal"]:
			product_query = query(sale, columns_requested+[("sum", sale, "RG_Net_Amount_WOTax_REF", sale, "MD_Net_Amount_WOTax_REF"), "DateNumYYYYMMDD", (boutique, "Description")], top_distinct= 'DISTINCT')
		elif query_type["croissance"]:
			product_query = query(sale, [("sum", sale, "RG_Net_Amount_WOTax_REF", sale, "MD_Net_Amount_WOTax_REF")])
		elif query_type["margin"]:
			product_query = query(sale, columns_requested + [("sum", sale, "RG_Net_Amount_WOTax_REF", sale, "MD_Net_Amount_WOTax_REF"),("sum", sale, 'Unit_Avg_Cost_REF')])
		elif query_type["quantity"]:
			product_query = query(sale, columns_requested)
		elif query_type["netsale"]:
			product_query = query(sale, columns_requested + [("sum", sale, "RG_Net_Amount_WOTax_REF", sale, "MD_Net_Amount_WOTax_REF")])
		else:
			product_query = query(sale, columns_requested + [("sum", sale, "RG_Net_Amount_WOTax_REF", sale, "MD_Net_Amount_WOTax_REF")])

		"""
		Jointures
		"""

		already_joined = []
		if len(self.boutiques) > 0 or query_type["exceptionnal"] or query_type["croissance"] or query_type["location"]:
			product_query.join(sale, boutique, "Location", "Code")
			already_joined.append("boutique")

		if query_type["nationality"]:
			product_query.join(sale, country, "Cust_Nationality", "Code_ISO")
			already_joined.append("country")

		if colour_query:
			product_query.join(sale, color, "Color", "Code")

		product_query = geography_joins(product_query, self.geo, already_joined = already_joined)
		product_query = sale_join_products(product_query, self.items)

		"""
		Conditions
		"""

		product_query.whereNotJDAandOTH()

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

		if not query_type["croissance"]:
			if len(self.numerical_dates) > 0:
				product_query.wheredate(sale, 'DateNumYYYYMMDD', self.numerical_dates[0][0], end=self.numerical_dates[0][1])
			else:
				product_query.wheredate(sale, 'DateNumYYYYMMDD') # par défaut sur les 7 derniers jours

		if query_type["exceptionnal"]:
			product_query.whereComparaison(sale, ("sum", sale, "RG_Net_Amount_WOTax_REF", sale, "MD_Net_Amount_WOTax_REF"), ">", str(self.seuil_exc))

		"""
		Finitions
		"""

		if query_type["colour"]:
			product_query.groupby(sale, 'Color')
			product_query.orderby(None, 'count(*)', " DESC")
		elif query_type["location"]:
			product_query.groupby(boutique, 'Description')
			product_query.orderby(None, 'count(*)', " DESC")
		elif query_type["exceptionnal"]:
			product_query.orderby(sale, ("sum", sale, "RG_Net_Amount_WOTax_REF", sale, "MD_Net_Amount_WOTax_REF"), "DESC")
		elif query_type["price"] or query_type["croissance"]:
			pass
		else:
			for col in column_groupby:
				product_query.groupby(col[0], col[1])


		"""
		On renvoit une réponse
		"""

		if query_type["colour"]:
			query_result = product_query.write().split('\n')
			print(query_result)
			result = [w.split("#")[0]+" ( "+w.split("#")[1]+" vendus )" for w in query_result if 'SALE_Color' not in w and '------' not in w]
			if len(result) > 0:
				if 'le plus' in self.sentence or 'la plus' in self.sentence:
					print("Wanting the top one from: ")
					print(result)
					result_string = "La couleur la plus vendue est "+result[0]+" pour "+",".join(front_products)
					print("retourne: "+result_string)
					if result_string[-1] == ",":
						result_string = result_string[:-1]
					return [product_query.request,result_string]
				else:
					return [product_query.request,"\n".join(result)]
			else:
				ret_string = "Aucune couleur enregistrée pour "
				for produit in self.items :
					for produit_key in produit:
						ret_string += produit[produit_key]+","
				if ret_string[-1] == ",":
					ret_string = ret_string[:-1]
				return [product_query.request,ret_string]

		elif query_type["location"]:
			query_result = product_query.write().split('\n')
			print(query_result)
			result = [w.split("#")[0]+" ( "+w.split("#")[1]+" vendus )" for w in query_result if 'LOCA_Description' not in w and '------' not in w]
			print(result)
			return [product_query.request,";;".join(result)]

		elif query_type["price"]:
			query_result = product_query.write().split('\n')
			print(query_result)
			result_line = query_result[1].split('#')
			item_price = round(float(result_line[0]), 2)

			details = append_details_date([], self.numerical_dates)
			details = append_details_products(details, self.items)
			details = append_details_geo(details, self.geo)

			print(result_line)
			result = str(item_price) + "€ HT."
			print(result)
			return [product_query.request,result,details]

		elif query_type["exceptionnal"]:

			query_result = product_query.write().split('\n')
			start_date = self.numerical_dates[0][0] if len(self.numerical_dates) > 0 else last_monday()


			result = "Il y a eu %i ventes exceptionnelles (supérieures à %s)" %(len(query_result)-1, affichage_euros(self.seuil_exc))
			result += "pour " + ', '.join(produit_selected) + " " if len(produit_selected) > 0 else ''
			result += "dans les boutiques " + ', '.join([b for b in self.boutiques]) if len(self.boutiques) > 0 else ''
			result += "\n"

			result += "Voici les 3 meilleures :" if len(query_result)-1 > 3 else ""

			for n, ligne in enumerate(query_result):
				if n > 0 and n < 4:
					colonnes = ligne.split('#')
					item_desc, item_prix, item_date, item_lieu = colonnes
					result += "%s vendu à %s le %s à %s\n" % (item_desc, affichage_euros(item_prix), affichage_date(item_date), item_lieu)

			print("***************")
			return [product_query.request, result]

		elif query_type["margin"]:
			query_result = product_query.write().split('\n')

			somme = 0
			details_items = []
			for n, ligne in enumerate(query_result):
				if n > 0:
					colonnes = ligne.split('#')
					nombre_ventes = colonnes[1]
					somme += float(nombre_ventes)
				if n > 0 and n < 10:
					details_items.append(colonnes)
				if n == 10:
					details_items.append(["...", "..."])
					break
			real_items = []
			margins = []
			total = 0
			for items in details_items:
				name = items[0]
				margin = (float(items[2])-float(items[3]))/float(items[2])
				margins.append({
					'margin': margin,
					'count': float(items[1])
				})
				total += float(items[1])
				real_items.append([name,str(math.ceil(margin*100000)/1000)+"%"])
			margin_global = 0
			for margin in margins:
				margin_global += margin['margin']*margin['count']/total

			result = "Margin: "+str(math.ceil(margin_global*100000)/1000)+"%"

			return [product_query.request, result, real_items]

		elif query_type["croissance"]:
			second_query = copy(product_query)
			if len(self.numerical_dates) > 1:
				product_query.wheredate(sale, 'DateNumYYYYMMDD', self.numerical_dates[0][0], self.numerical_dates[0][1])
				second_query.wheredate(sale, 'DateNumYYYYMMDD', self.numerical_dates[1][0], self.numerical_dates[1][1])
			else:
				product_query.wheredate(sale, 'DateNumYYYYMMDD') # par défaut sur les 7 derniers jours
				second_query.wheredate(sale, 'DateNumYYYYMMDD', "20170218", "20170225") # TODO : à changer
			ventes_n = product_query.write().split('\n')
			ventes_n_moins_un = second_query.write().split('\n')
			vente_date_n = ventes_n[1]
			vente_date_n_moins_un = ventes_n_moins_un[1]

			if vente_date_n_moins_un == "NULL" or vente_date_n == "NULL":
				result = "Aucune vente enregistrée "
			else:
				vente_date_n = float(vente_date_n)
				vente_date_n_moins_un = float(vente_date_n_moins_un)
				croissance = 100 * (vente_date_n - vente_date_n_moins_un) / vente_date_n_moins_un if vente_date_n_moins_un > 0 else 0
				print("Croissance calculée, ", croissance)
				result = "La croissance est de %.2f%% " %(croissance)

			start_date = self.numerical_dates[0][0] if len(self.numerical_dates) > 0 else '20170225'
			second_start_date = self.numerical_dates[1][0] if len(self.numerical_dates) > 1 else '20170218'

			# result += "du %s au %s par rapport au %s au %s " %(start_date, "20170304", second_start_date, start_date)
			# result += "pour " + ', '.join(produit_selected) + " " if len(produit_selected) > 0 else ''
			# result += "dans les boutiques de " + ', '.join([b for b in self.boutiques]) if len(self.boutiques) > 0 else ''

			details = append_details_date([], self.numerical_dates)
			details = append_details_products(details, self.items)
			details = append_details_geo(details, self.geo)

			print("***************")
			return [product_query.request, result, details]

		elif query_type["quantity"]:
			query_result = product_query.write().split('\n')

			details = append_details_date([], self.numerical_dates)
			somme = 0
			for n, ligne in enumerate(query_result):
				if n == 0:
					colonnes = ligne.split('#')
					categorie = find_category(colonnes[0])
				if n > 0:
					colonnes = ligne.split('#')
					nombre_ventes = colonnes[len(colonnes)-1]
					somme += int(nombre_ventes)
				if n > 0 and n < 10:
					details.append([categorie + " " + colonnes[0], colonnes[len(colonnes)-1]])
				if n == 10:
					details.append(["...", "..."])
					break
			print(details)

			result = "Il y a eu " + str(somme) + " ventes "# en lien avec " + " et/ou ".join(produit_selected) + " "
			result += text_MDorFP
			# result += "dans les boutiques de " + ', '.join([b for b in self.boutiques]) + " " if len(self.boutiques) > 0 else ''

			print("***************")
			return [product_query.request, result, details]


		elif query_type["netsale"]:
			query_result = product_query.write().split('\n')

			details = append_details_date([], self.numerical_dates)
			details = append_details_products(details, self.items)
			details = append_details_geo(details, self.geo)

			somme = 0
			for n, ligne in enumerate(query_result):
				if n == 0:
					colonnes = ligne.split('#')
					categorie = find_category(colonnes[0])
				elif n > 0:
					colonnes = ligne.split('#')
					prix_ventes = colonnes[len(colonnes)-1]
					somme += float(prix_ventes)
				if n > 0 and n < 10:
					details.append([categorie + " " + colonnes[0], affichage_euros(colonnes[len(colonnes)-1])])
				if n == 10:
					details.append(["...", "..."])
					break
			print(details)


			result = "Il y a eu " + affichage_euros(str(somme)) + " HT de CA en lien avec " + " et/ou ".join(produit_selected) + " "
			result += text_MDorFP
			result += "dans les boutiques de " + ', '.join([b for b in self.boutiques]) if len(self.boutiques) > 0 else ''

			print("***************")
			return [product_query.request, result, details]

		else:
			query_result = product_query.write().split('\n')

			details = append_details_date([], self.numerical_dates)

			valeur = 0
			quantite = 0
			for n, ligne in enumerate(query_result):
				if n == 0:
					colonnes = ligne.split('#')
					categorie = find_category(colonnes[0])
				if n > 0:
					colonnes = ligne.split('#')
					prix_ventes = colonnes[len(colonnes)-1]
					quantite_ventes = colonnes[len(colonnes)-2]
					valeur += float(prix_ventes)
					quantite += int(quantite_ventes)
				if n > 0 and n < 10:
					details.append([categorie + ' ' + colonnes[0], "("+quantite_ventes+" vendu pour "+affichage_euros(prix_ventes)+" HT"])
				if n == 10:
					details.append(["...", "..."])
					break

			details = append_details_boutiques(details, self.boutiques)
			print(details)

			result = "Il y a eu " + str(quantite) + " ventes pour un total de " + affichage_euros(str(valeur)) + " HT "
			result += text_MDorFP

			print("***************")
			return [product_query.request, result, details]

"""
data = {
		'cities' : ['Paris', 'Madrid'],
		'countries' : [],
		'nationalities' : [],
		'dates' : [],
		'numerical_dates' : [],
		'sentence' : '',
		'items' : {'produit':['robe']}
		}

test = Produit(data)
print(test.build_query())
"""
