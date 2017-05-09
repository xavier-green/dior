# Pour pouvoir importer les fichiers sql
# from importlib.machinery import SourceFileLoader

# foo = SourceFileLoader("sql.request", "../sql/request.py").load_module()
# foo = SourceFileLoader("sql.tables", "../sql/tables.py").load_module()


from sql.request import query

# Import de toutes les tables utilisées
from sql.tables import item, sale, boutique, country, division, retail, theme, department, zone, stock_daily

class Stock(object):

	def __init__(self, data):
		self.cities = data['cities']
		self.countries = data['countries']
		self.nationalities = data['nationalities']
		self.dates = data['dates']
		self.numerical_dates = data['numerical_dates']
		self.items = data['items']
		self.boutiques = data['boutiques']
		self.sentence = data['sentence']

	def build_answer(self):
		response_base = self.build_query()
		print(response_base)
		# response_complete = self.append_details(response_base[1])
		return [response_base[0],response_base[1]]


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

		if len(self.items) > 0:
			stock_query.join(stock_daily, item, "Style", "Code") # jselointure sur ITEM_Code = STOC_Style

		if len(self.cities) > 0:
			stock_query.join(stock_daily, boutique, "Location", "Code") # jointure sur STOC_Location = LOCA_Code

		elif len(self.countries) > 0:
			stock_query.join(stock_daily, country, "Country", "Code") # jointure sur STOC_Country = COUN_Code

		"""
		Conditions
		"""

		liste_item = []
		for produit in self.items :
			for produit_key in produit:
				stock_query.where(item, "Description", produit[produit_key])
				liste_item.append(produit[produit_key])

		for ville in self.cities :
			stock_query.where(boutique, "Description", ville)

		if len(self.cities) == 0:
			for pays in self.countries :
				stock_query.where(country, "Description_FR", pays)


		"""
		Traitement de la réponse
		"""

		res_stock = stock_query.write()

		if not sellthru_query:
			response = "Le stock concernant les mots-clés " + ", ".join(liste_item) + " est de " + res_stock
			return(stock_query.request, response)





		if 'NULL' in res_stock:
			res_stock = 0
		else:
			res_stock = int(res_stock)
		print('Stock:', res_stock)


		if 'sellthru' in self.sentence:
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
			# Retirer Jardin D'avron et Others
			product_query.join(sale, zone, 'Zone', 'Code')

			if 'couleur' in self.sentence:
				product_query = query(sale, ['Color','count(*)'], top_distinct='DISTINCT TOP 5')
			elif ('Où' in self.sentence) or ('où' in self.sentence):
				product_query = query(sale, [(boutique, 'Description'),'count(*)'], top_distinct='DISTINCT TOP 5')
			# Initialisation de la query : par défaut pour l'instant on sélectionne count(*)	'""'
			if len(self.items) > 0:
				product_query.join(sale, item, "Style", "Code") # jointure sur ITEM_Code = SALE_Style
			product_query.join(sale, boutique, "Location", "Code") # jointure sur SALE_Location = LOCA_Code

			# S'il n'y a pas de ville, on s'intéresse au pays
			if len(self.countries) > 0:
				product_query.join(sale, country, "Country", "Code") # jointyre sur SALE_Country = COUN_Code

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

			product_query.whereNotJDAandOTH()

			for ville in self.cities :
				product_query.where(boutique, "Description", ville)

			if len(self.cities) == 0:
				for pays in self.countries :
					product_query.where(country, "Description_FR", pays)

			if len(self.numerical_dates) > 0:
				product_query.wheredate(sale, 'DateNumYYYYMMDD', self.numerical_dates[0][0], self.numerical_dates[0][1])
			else:
				product_query.wheredate(sale, 'DateNumYYYYMMDD') # par défaut sur les 7 derniers jours
				# La requête est terminée, on l'écrit
				# product_query.write()
			res_sales = product_query.write()
			if res_sales == 'NULL':
				res_sales = 0
			else:
				res_sales = int(res_sales)
			print("Sales:", res_sales)
			sellthru = format((100 * res_sales / (res_sales  + res_stock)), '.2f') + ' %'
			res_sellthru = 'Le sellthru '
			if len(self.boutiques) > 0:
				res_sellthru += "dans la boutique " + ' '.join(self.boutiques) + ' '
			if len(self.cities) > 0:
				res_sellthru += "dans la ville "  + ' '.join(self.cities) + ' '
			if len(self.countries) > 0:
				res_sellthru += 'dans le pays ' + ' '.join(self.countries) + ' '
			res_sellthru += "est de " + sellthru
			return [stock_query.request + '\n' + product_query.request,res_sellthru ]
			str_res_stock = 'Le stock '
			if len(self.boutiques) > 0:
				str_res_stock += "dans la boutique " + ' '.join(self.boutiques) + ' '
			if len(self.cities) > 0:
				str_res_stock += "dans la ville "  + ' '.join(self.cities) + ' '
			if len(self.countries) > 0:
				str_res_stock += 'dans le pays ' + ' '.join(self.countries) + ' '
			res_sellthru += "est de " + str(res_stock)
			return(stock_query.request, str_res_stock)
		return(stock_query.request, res_stock)
