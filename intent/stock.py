﻿from sql.request import query

# Import de toutes les tables utilisées
from sql.tables import item, sale, boutique, country, division, retail, theme, department, zone, stock_daily, zone, uzone, sub_zone, collection, collectiondate

from annexes.mise_en_forme import affichage_euros, affichage_date, separateur_milliers
from annexes.gestion_geo import geography_joins, geography_select
from annexes.gestion_products import what_products, sale_join_products, query_products, where_products
from annexes.gestion_details import append_details_date, append_details_products, append_details_geo, find_category, append_details_boutiques
from annexes.gestion_intent_vente import find_MDorFP
from extraction.date import monthDifference, lastThreeMonth

class Stock(object):

	def __init__(self, data):
		self.geo = data['geo']
		# self.nationalities = data['nationalities']
		self.dates = data['dates']
		self.numerical_dates = data['numerical_dates']
		self.items = data['items']
		self.boutiques = data['boutiques']
		self.sentence = data['sentence']
		self.product_sources = data['sources']

	def build_answer(self):
		response_base = self.build_query()
		print(response_base)
		details_query = response_base[2] if len(response_base) > 2 else "No details"

		# response_complete = self.append_details(response_base[1])
		return [response_base[0],response_base[1], details_query]


	def build_query(self):

		"""
		Détermine s'il s'agit d'une demande de stock ou de couverture de stock ou de sellthru
		"""

		couv_query = False
		thru_query = False

		if 'couverture' in self.sentence:
			print('It is a couverture')
			couv_query = True

		if 'thru' in self.sentence:
			print('It is a sellthru')
			thru_query = True
		
		"""
		Initialisation de la query
		"""

		stock_query = query(stock_daily, [('sum', stock_daily, 'Quantity'), "DateNumYYYYMMDD"], top_distinct='TOP 1')

		"""
		Jointures
		"""

		stock_query = sale_join_products(stock_query, self.items, main_table = stock_daily)
		stock_query = geography_joins(stock_query, self.geo, main_table = stock_daily)

		if len(self.boutiques) > 0 :
			stock_query.join(stock_daily, boutique, "Location", "Code")


		"""
		Conditions
		"""

		stock_query = where_products(stock_query, self.items)
		stock_query = geography_select(stock_query, self.geo)

		for _boutique in self.boutiques:
			stock_query.where(boutique, "Description", _boutique)

		"""
		Traitement de la réponse
		"""

		stock_query.groupby(stock_daily, "DateNumYYYYMMDD")
		stock_query.orderby(stock_daily, "DateNumYYYYMMDD", "DESC")

		result_query = stock_query.write().split("\n")
		
		if len(result_query)<2:
			return(stock_query.request, 'Pas de stock trouvé', append_details_boutiques(append_details_geo(append_details_products([], self.items, self.product_sources), self.geo),self.boutiques))
		else:
			result_query = result_query[1].split('#')
			print(result_query)
			res_stock = result_query[0]
			res_date = result_query[1]
		print(res_date)
		details = append_details_date([], [[res_date, res_date]])
		details = append_details_products(details, self.items, self.product_sources)
		details = append_details_geo(details, self.geo)
		details = append_details_boutiques(details, self.boutiques)

		if not couv_query and not thru_query:
			if 'NULL' in res_stock:
				res_stock = "Le stock est de 0"
			else:
				res_stock = "Le stock est de " + separateur_milliers(res_stock)
			return([stock_query.request, res_stock, details])

		if 'NULL' in res_stock:
			res_stock = 0
		else:
			res_stock = int(res_stock)
		print('Stock:', res_stock)

		"""
		Query secondaire pour la couverture de stock
		Il faut ici calculer les sales en plus du stock
		"""

		if couv_query:
			print('It is a couv')
			
			# Initialisation

			MDorFP, Quantity = find_MDorFP(self.sentence)
			product_query = query(sale, [Quantity])

			# Jointures

			product_query = geography_joins(product_query, self.geo)
			product_query = sale_join_products(product_query, self.items)

			if len(self.boutiques) > 0 :
				product_query.join(sale, boutique, "Location", "Code")

			# Conditions

			product_query = where_products(product_query, self.items)
			product_query = geography_select(product_query, self.geo)

			for _boutique in self.boutiques:
				product_query.where(boutique, "Description", _boutique)

			product_query.whereNotJDAandOTH()

			if len(self.numerical_dates) == 0:
				# Default to last 3 months
				self.numerical_dates = [lastThreeMonth()]

			product_query.wheredate(sale, 'DateNumYYYYMMDD', self.numerical_dates[0][0], self.numerical_dates[0][1])

			# Calcul des ventes

			res_sales = product_query.write()
			if 'NULL' in res_sales:
				res_sales = 0
			else:
				res_sales = int(res_sales)

			print("Sales:", res_sales)
			
			# Moyenne des ventes sur 1 mois
			
			moy_sales = res_sales / monthDifference(self.numerical_dates[0][0], self.numerical_dates[0][1])
			# Details
			details = append_details_date([], self.numerical_dates)
			details = append_details_products(details, self.items, self.product_sources)
			details = append_details_geo(details, self.geo)
			details = append_details_boutiques(details, self.boutiques)


			# Calcul de la couverture de stock
			if res_stock == 0:
				return [stock_query.request + '\n' + product_query.request,"Pas de stock trouvé. La couverture de stock est indéterminée", details]
			if moy_sales > 0:
				couv = (res_stock)/(moy_sales)
				res_couv = "La couverture de stock est de %.2f mois" %(couv)
				return [stock_query.request + '\n' + product_query.request,res_couv, details]
			str_res_stock = "Pas de ventes, la couverture de stock est indéderminée"
			return(stock_query.request + '\n' + product_query.request, str_res_stock, details)


		# Sellthru query
		elif thru_query:
			collec = ""
			for x in self.items:
				if 'collection' in x.keys():
					collec = x['collection']
			if collec == "":
				return("", "Pas de collection trouvée. Merci d'en préciser une.", details)

			
			# Requete pour avoir la date de début
			date_query = query(collectiondate, ['Sale_date_deb', 'Sale_date_fin'], top_distinct='TOP 1')
			date_query.join(collectiondate, collection, "Code", "Code")
			date_query.where(collection, "Description", collec)
			date_query.orderby(collectiondate, "Sale_date_deb", "DESC")
			res_date = date_query.write().split('\n')
			print(res_date)
			if len(res_date) < 2:
				return(date_query.request, "Erreur pendant la recherche des dates de la collection", details)
			self.numerical_dates = [res_date[1].split('#')]
			print(self.numerical_dates)
			
			product_query = query(sale, [('sum', sale, 'RG_Quantity'), ("sum", sale, 'MD_Quantity')])
			# Jointures

			product_query = geography_joins(product_query, self.geo)
			product_query = sale_join_products(product_query, self.items)

			if len(self.boutiques) > 0 :
				product_query.join(sale, boutique, "Location", "Code")

			# Conditions

			product_query = where_products(product_query, self.items)
			product_query = geography_select(product_query, self.geo)

			for _boutique in self.boutiques:
				product_query.where(boutique, "Description", _boutique)

			product_query.whereNotJDAandOTH()

			if len(self.numerical_dates) == 0:
				# Default to last 3 months
				self.numerical_dates = [lastThreeMonth()]

			product_query.wheredate(sale, 'DateNumYYYYMMDD', self.numerical_dates[0][0], self.numerical_dates[0][1])

			# Calcul des ventes

			res_sales = product_query.write().split('\n')[1].split('#')

			print("Sales:", res_sales)
			sales_FP = 0
			sales_MD = 0
			if res_sales[0] != 'NULL':
				sales_FP = int(res_sales[0])
			if res_sales[1] != 'NULL':
				sales_MD = int(res_sales[0])

			print("Sales:", res_sales)

			# Details
			details = append_details_date([], self.numerical_dates)
			details = append_details_products(details, self.items, self.product_sources)
			details = append_details_geo(details, self.geo)
			details = append_details_boutiques(details, self.boutiques)
			
			if res_stock + sales_FP + sales_MD ==0:
				return(stock_query.request +'\n'+ date_query.request + '\n'+ product_query.request, 'Pas de ventes ni de stocks trouvés', details)
			res_sellthru = (100 * sales_FP) / (sales_FP + sales_MD + res_stock)
			return(date_query.request+'\n'+ stock_query.request + '\n'+ product_query.request, 'Le sellthru est de %.2f%%' %(res_sellthru), details)
			

