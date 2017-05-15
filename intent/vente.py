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

# Import de toutes les tables utilisées
from sql.tables import item, sale, boutique, country, division, retail, theme, department, zone, uzone, sub_zone

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

		location_query = False
		colour_query = False
		price_query = False
		exceptionnal_query = False
		croissance_query = False
		margin_query = False
		nationality_query = False
		quantity_query = False
		netsale_query = False
		touriste = False

		first_word = self.sentence.split(" ")[0]
		question = self.sentence.lower()

		if ('Où' in self.sentence) or ('où' in self.sentence) or (first_word == "ou") or (first_word == "Ou") or ('dans quel pays' in self.sentence.lower()) or ('a quel endroit' in self.sentence.lower()):
			print("Sale specific to a location")
			location_query = True

		if ('couleur' in question):
			print("Sale specific to a colour")
			colour_query = True

		if ('prix' in question):
			print("Sale specific to a price")
			price_query = True

		if ('exceptionnel' in question):
			if self.seuil_exc:
				print("Sale specific to exceptionnal sales")
				exceptionnal_query = True
			else:
				self.seuil_exc = 5000
				print("Sale specific to exceptionnal sales, default seuil at 5k")
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

		Quantity_requested = []
		if 'fp' in question or ('full' in question and 'price' in question):
			Quantity_requested.append('fp')
		if 'md' in question or ('mark' in question and 'down' in question):
			Quantity_requested.append('md')

		if len(Quantity_requested) == 0 or len(Quantity_requested) == 2:
			Quantity = ('sum', sale, 'RG_Quantity', sale, 'MD_Quantity')
			MDorFP = ""
		elif Quantity_requested[0] == 'fp':
			Quantity = ('sum', sale, 'RG_Quantity')
			MDorFP = "en Full Price "
		else:
			Quantity = ('sum', sale, 'MD_Quantity')
			MDorFP = "en Mark Down "

		# List in what categories we will be looking
		columns_requested = query_products(self.items)
		column_groupby = columns_requested[:]
		columns_requested.append(Quantity)

		"""
		On créé la query en fonction de la question
		"""

		if colour_query:
			product_query = query(sale, ['Color', 'count(*)'], top_distinct='DISTINCT TOP 5')
		elif location_query:
			product_query = query(sale, [(boutique, 'Description'), 'count(*)'], top_distinct='DISTINCT TOP 5')
		elif price_query:
			product_query = query(sale, [(sale, "RG_Net_Amount_WOTax_REF")], top_distinct='DISTINCT TOP 1')
		elif exceptionnal_query:
			product_query = query(sale, columns_requested+[("sum", sale, "RG_Net_Amount_WOTax_REF", sale, "MD_Net_Amount_WOTax_REF"), "DateNumYYYYMMDD", (boutique, "Description")], top_distinct= 'DISTINCT')
		elif croissance_query:
			product_query = query(sale, [("sum", sale, "RG_Net_Amount_WOTax_REF", sale, "MD_Net_Amount_WOTax_REF")])
		elif margin_query:
			product_query = query(sale, columns_requested + [("sum", sale, "RG_Net_Amount_WOTax_REF", sale, "MD_Net_Amount_WOTax_REF"),("sum", sale, 'Unit_Avg_Cost_REF')])
		elif quantity_query:
			product_query = query(sale, columns_requested)
		elif quantity_query:
			product_query = query(sale, columns_requested + [("sum", sale, "RG_Net_Amount_WOTax_REF", sale, "MD_Net_Amount_WOTax_REF")])
		else:
			product_query = query(sale, columns_requested + [("sum", sale, "RG_Net_Amount_WOTax_REF", sale, "MD_Net_Amount_WOTax_REF")])

		"""
		On fait les join
		"""

		product_query = geography_joins(sale, product_query, self.geo)

		if len(self.boutiques) > 0 or exceptionnal_query or croissance_query or location_query > 0:
			product_query.join(sale, boutique, "Location", "Code")

		# if len(self.countries) > 0:
		# 	product_query.join(sale, country, "Country", "Code")

		if nationality_query:
			product_query.join(sale, country, "Cust_Nationality", "Code_ISO")

		product_query = sale_join_products(product_query, self.items)

		"""
		On fait les conditions
		"""

		product_query.whereNotJDAandOTH()

		front_products = []

		produit_selected = []
		for produit in self.items :
			for produit_key in produit:
				front_products.append(produit[produit_key])
				if produit_key == "division":
					product_query.where(division, "Description", produit[produit_key])
					produit_selected.append("la division " + produit[produit_key])
				elif produit_key == "departement":
					product_query.where(department, "Description", produit[produit_key])
					produit_selected.append("le departement " + produit[produit_key])
				elif produit_key == "groupe":
					product_query.where(retail, "Description", produit[produit_key])
					produit_selected.append("le groupe retail " + produit[produit_key])
				elif produit_key == "theme":
					product_query.where(theme, "Description", produit[produit_key])
					produit_selected.append("le theme " + produit[produit_key])
				elif produit_key == "produit":
					product_query.where(item, "Description", produit[produit_key])
					produit_selected.append("le produit " + produit[produit_key])

		if nationality_query:
			if touriste:
				product_query.whereComparaison(sale, "Country", "<>", "CO.COUN_Code")
			else:
				product_query.whereComparaison(sale, "Country", "=", "CO.COUN_Code")


		product_query = geography_select(product_query, self.geo)

		# for ville in self.cities :
		# 	product_query.where(boutique, "Description", ville)

		# if len(self.cities) == 0:
		# 	for pays in self.countries :
		# 		product_query.where(country, "Description_FR", pays)

		if len(self.boutiques) > 0:
			for _boutique in self.boutiques :
				product_query.where(boutique, "Description", _boutique)

		if not croissance_query:
			if len(self.numerical_dates) > 0:
				product_query.wheredate(sale, 'DateNumYYYYMMDD', self.numerical_dates[0][0], end=self.numerical_dates[0][1])
			else:
				product_query.wheredate(sale, 'DateNumYYYYMMDD') # par défaut sur les 7 derniers jours


		"""
		On renvoit une réponse
		"""

		if colour_query:
			product_query.groupby(sale, 'Color')
			product_query.orderby(None, 'count(*)', " DESC")
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

		elif location_query:
			product_query.groupby(boutique, 'Description')
			product_query.orderby(None, 'count(*)', " DESC")
			query_result = product_query.write().split('\n')
			print(query_result)
			result = [w.split("#")[0]+" ( "+w.split("#")[1]+" vendus )" for w in query_result if 'LOCA_Description' not in w and '------' not in w]
			print(result)
			return [product_query.request,";;".join(result)]

		elif price_query:
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

		elif exceptionnal_query:
			product_query.whereComparaison(sale, ("sum", sale, "RG_Net_Amount_WOTax_REF", sale, "MD_Net_Amount_WOTax_REF"), ">", str(self.seuil_exc))
			product_query.orderby(sale, ("sum", sale, "RG_Net_Amount_WOTax_REF", sale, "MD_Net_Amount_WOTax_REF"), "DESC")

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

		elif margin_query:
			for col in column_groupby:
				product_query.groupby(col[0], col[1])
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

		elif croissance_query:
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

		elif quantity_query:
			for col in column_groupby:
				product_query.groupby(col[0], col[1])
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
			result += MDorFP
			# result += "dans les boutiques de " + ', '.join([b for b in self.boutiques]) + " " if len(self.boutiques) > 0 else ''

			print("***************")
			return [product_query.request, result, details]


		elif netsale_query:
			for col in column_groupby:
				product_query.groupby(col[0], col[1])
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
			result += MDorFP
			result += "dans les boutiques de " + ', '.join([b for b in self.boutiques]) if len(self.boutiques) > 0 else ''

			print("***************")
			return [product_query.request, result, details]

		else:
			for col in column_groupby:
				product_query.groupby(col[0], col[1])
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
			result += MDorFP

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
