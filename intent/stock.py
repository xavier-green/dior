# Pour pouvoir importer les fichiers sql
# from importlib.machinery import SourceFileLoader

# foo = SourceFileLoader("sql.request", "../sql/request.py").load_module()
# foo = SourceFileLoader("sql.tables", "../sql/tables.py").load_module()


from sql.request import query

# Import de toutes les tables utilisées
from sql.tables import item, sale, boutique, country, division, retail, theme, department, zone, stock_daily, zone, uzone, sub_zone

from annexes.mise_en_forme import affichage_euros, affichage_date
from annexes.gestion_geo import geography_joins, geography_select
from annexes.gestion_products import what_products, sale_join_products, query_products, where_products
from annexes.gestion_details import append_details_date, append_details_products, append_details_geo, find_category

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
		Détermine s'il s'agit d'une demande de stock ou de sellthru
		"""

		sellthru_query = False

		if 'sellthru' in self.sentence:
			print('It is a sellthru')
			sellthru_query = True

		"""
		Initialisation de la query
		"""

		stock_query = query(stock_daily, [('sum', stock_daily, 'Quantity')])

		"""
		Jointures
		"""
		stock_query = sale_join_products(stock_query,self.items,main_table=stock_daily)

		# GEOGRAPHY Extraction

		stock_query = geography_joins(stock_query, self.geo, main_table=stock_daily)

		"""
		Conditions
		"""

		stock_query = where_products(stock_query, self.items)


		stock_query = geography_select(stock_query, self.geo)


		"""
		Traitement de la réponse
		"""

		res_stock = stock_query.write().replace("\n","")

		details = append_details_date([], self.numerical_dates)
		details = append_details_products(details, self.items, self.product_sources)
		details = append_details_geo(details, self.geo)

		if not sellthru_query:
			if 'NULL' in res_stock:
				res_stock = "Le stock est de 0"
			else:
				res_stock = "Le stock est de " + res_stock
			return([stock_query.request, str_res_stock, details])

		if 'NULL' in res_stock:
			res_stock = 0
		else:
			res_stock = int(res_stock)
		print('Stock:', res_stock)

		if sellthru_query:
			print('It is a sellthru')
			#Calculate sales for sellthru
			Quantity_requested = []
			if 'fp' in self.sentence.lower() or ('full' in self.sentence.lower() and 'price' in self.sentence.lower()):
				Quantity_requested.append('fp')
			if 'md' in self.sentence.lower() or ('mark' in self.sentence.lower() and 'down' in self.sentence.lower()):
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

			product_query = query(sale, [Quantity])

			if 'couleur' in self.sentence:
				product_query = query(sale, ['Color','count(*)'], top_distinct='DISTINCT TOP 5')
			elif ('Où' in self.sentence) or ('où' in self.sentence):
				product_query = query(sale, [(boutique, 'Description'),'count(*)'], top_distinct='DISTINCT TOP 5')
			# Initialisation de la query : par défaut pour l'instant on sélectionne count(*)	'""'
			if len(self.items) > 0:
				product_query.join(sale, item, "Style", "Code") # jointure sur ITEM_Code = SALE_Style
			product_query.join(sale, boutique, "Location", "Code") # jointure sur SALE_Location = LOCA_Code

			product_query = geography_joins(product_query, self.geo)

			# Maintenant que toutes les jointures sont faites, on passe aux conditions
			for produit in self.items :
				for produit_key in produit:
					if produit_key == "division":
						product_query.join(sale, division,"Division","Code")
						product_query.where(division, "Description", produit[produit_key])
					elif produit_key == "departement":
						product_query.join(sale, department,"Department","Code")
						product_query.where(department, "Description", produit[produit_key])
					elif produit_key == "groupe":
						product_query.join(sale, retail,"Group","Code")
						product_query.where(retail, "Description", produit[produit_key])
					elif produit_key == "theme":
						product_query.join(sale, theme,"Theme","Code")
						product_query.where(theme, "Description", produit[produit_key])
					elif produit_key == "produit":
						product_query.where(item, "Description", produit[produit_key])

			product_query = geography_select(product_query, self.geo)
			product_query.whereNotJDAandOTH()

			if len(self.numerical_dates) > 0:
				product_query.wheredate(sale, 'DateNumYYYYMMDD', self.numerical_dates[0][0], self.numerical_dates[0][1])
			else:
				product_query.wheredate(sale, 'DateNumYYYYMMDD') # par défaut sur les 7 derniers jours
				# La requête est terminée, on l'écrit
				# product_query.write()
			res_sales = product_query.write()
			if 'NULL' in res_sales:
				res_sales = 0
			else:
				res_sales = int(res_sales)
			print("Sales:", res_sales)
			if (res_sales+res_stock > 0):
				sellthru = format((100 * res_sales / (res_sales  + res_stock)), '.2f') + ' %'
				res_sellthru = 'Le sellthru '
				if len(self.boutiques) > 0:
					res_sellthru += "dans la boutique " + ' '.join(self.boutiques) + ' '
				res_sellthru += "est de " + sellthru
				return [stock_query.request + '\n' + product_query.request,res_sellthru, details]
			str_res_stock = "Le stock est null"
			return(stock_query.request + '\n' + product_query.request, str_res_stock, details)
