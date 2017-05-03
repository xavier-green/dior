"""
from importlib.machinery import SourceFileLoader

foo = SourceFileLoader("sql.request", "../sql/request.py").load_module()
foo = SourceFileLoader("sql.tables", "../sql/tables.py").load_module()

"""
from copy import copy

from sql.request import query

# Import de toutes les tables utilisées
from sql.tables import item, sale, boutique, country, division, retail, theme, department, zone


class Vente(object):

	def __init__(self, data):
		self.cities = data['cities']
		self.countries = data['countries']
		self.nationalities = data['nationalities']
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

		location_query = False
		colour_query = False
		price_query = False
		exceptionnal_query = False
		croissance_query = False
		margin_query = False
		nationality_query = False
		touriste = False

		first_word = self.sentence.split(" ")[0]

		if ('Où' in self.sentence) or ('où' in self.sentence) or ('ou' in first_word) or ('Ou' in first_word) or ('dans quel pays' in self.sentence.lower()) or ('a quel endroit' in self.sentence.lower()):
			print("Sale specific to a location")
			location_query = True

		if ('couleur' in self.sentence.lower()):
			print("Sale specific to a colour")
			colour_query = True

		if ('prix' in self.sentence.lower()):
			print("Sale specific to a price")
			price_query = True
		
		if ('exceptionnel' in self.sentence.lower()):
			if self.seuil_exc:
				print("Sale specific to exceptionnal sales")
				exceptionnal_query = True
			else:
				self.seuil_exc = 50000
				print("Sale specific to exceptionnal sales, default seuil at 50k")
				exceptionnal_query = True

		if ('margin' in self.sentence.lower()):
			margin_query = True
		
		if ('croissance' in self.sentence.lower()):
			print("Sale specific to a croissance")
			croissance_query = True

		if ('local' in self.sentence.lower() or 'locaux' in self.sentence.lower()):
			nationality_query = True
			
		if ('touriste' in self.sentence.lower()):
			nationality_query = True
			touriste = True

		if (not croissance_query or not exceptionnal_query) and len(self.items) == 0:
			return "Veuillez préciser un produit svp"

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

		# List in what categories we will be looking
		columns_requested = []
		for produit in self.items :
			for produit_key in produit:
				if produit_key == "division":
					column_groupby = (division, "Description")
					columns_requested.append((division, "Description"))
					break
				elif produit_key == "departement":
					column_groupby = (department, "Description")
					columns_requested.append((department, "Description"))
					break
				elif produit_key == "groupe":
					column_groupby = (retail, "Description")
					columns_requested.append((retail, "Description"))
					break
				elif produit_key == "theme":
					column_groupby = (theme, "Description")
					columns_requested.append((theme, "Description"))
					break
				if produit_key == "produit":
					column_groupby = (item, "Description")
					columns_requested.append((item, "Description"))
					break
		columns_requested.append(Quantity)

		if colour_query:
			product_query = query(sale, ['Color', 'count(*)'], top_distinct='DISTINCT TOP 5')
		elif location_query:
			product_query = query(sale, [(boutique, 'Description'), 'count(*)'], top_distinct='DISTINCT TOP 5')
		elif price_query:
			product_query = query(sale, [(item, 'Description'), 'Std_RP_WOTax_REF'], top_distinct='DISTINCT TOP 1')
		elif exceptionnal_query:
			product_query = query(sale, [(item, 'Description'), 'Std_RP_WOTax_REF', "DateNumYYYYMMDD", (boutique, "Description")], top_distinct= 'DISTINCT TOP 3')
		elif croissance_query:
			product_query = query(sale, [("sum", sale, 'Std_RP_WOTax_REF')])
		elif margin_query:
			product_query = query(sale, [("sum", sale, 'Std_RP_WOTax_REF'),("sum", sale, 'Unit_Avg_Cost_REF')])
		else:
			product_query = query(sale, columns_requested)

		product_query.join(sale, item, "Style", "Code")

		if len(self.boutiques) > 0:
			product_query.join(sale, boutique, "Location", "Code")

		if len(self.countries) > 0:
			product_query.join(sale, country, "Country", "Code")

		if nationality_query:
			product_query.join(sale, country, "Cust_Nationality", "Code_ISO")

		division_seen = False
		department_seen = False
		retail_seen = False
		theme_seen = False
		produit_seen = False

		for produit in self.items :
			for produit_key in produit:
				if produit_key == "division" and not division_seen:
					product_query.join(sale, division,"Division","Code")
					division_seen = True
				elif produit_key == "departement" and not department_seen:
					product_query.join(sale, department,"Department","Code")
					department_seen = True
				elif produit_key == "groupe" and not retail_seen:
					product_query.join(sale, retail,"Group","Code")
					retail_seen = True
				elif produit_key == "theme" and not theme_seen:
					product_query.join(sale, theme,"Theme","Code")
					theme_seen = True
				elif produit_key == "produit" and not produit_seen:
					# product_query.join(sale, item,"Style","Code")
					produit_seen = True

		# Retirer Jardin D'avron et Others
		product_query.join(sale, zone, 'Zone', 'Code')
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

		for ville in self.cities :
			product_query.where(boutique, "Description", ville)

		if len(self.cities) == 0:
			for pays in self.countries :
				product_query.where(country, "Description_FR", pays)

		if len(self.boutiques) > 0:
			for _boutique in self.boutiques :
				product_query.where(boutique, "Description", _boutique)

		if not croissance_query:
			if len(self.numerical_dates) > 0:
				product_query.wheredate(sale, 'DateNumYYYYMMDD', self.numerical_dates[0])
			else:
				product_query.wheredate(sale, 'DateNumYYYYMMDD') # par défaut sur les 7 derniers jours

		if colour_query:
			product_query.groupby(sale, 'Color')
			product_query.orderby(None, 'count(*)', " DESC")
			query_result = product_query.write().split('\n')
			print(query_result)
			result = [w.split("|")[0]+" ( "+w.split("|")[1]+" vendus )" for w in query_result if 'SALE_Color' not in w and '------' not in w]
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
					return [product_query.request,";;".join(result)]
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
			result = [w.split("|")[0]+" ( "+w.split("|")[1]+" vendus )" for w in query_result if 'LOCA_Description' not in w and '------' not in w]
			print(result)
			return [product_query.request,";;".join(result)]

		elif price_query:
			query_result = product_query.write().split('\n')
			result_line = query_result[1].split('|')
			item_desc = result_line[0]
			item_price = result_line[1]
			print(result_line)
			result = "L'item " + item_desc + " correspondant " + " et ".join(produit_selected) + " se vend à " + item_price + " euros HT."
			print(result)
			return [product_query.request,result]
		
		elif exceptionnal_query:
			product_query.whereComparaison(sale, "Std_RP_WOTax_REF", ">", str(self.seuil_exc))
			product_query.orderby(sale, "Std_RP_WOTax_REF", "DESC")
			
			query_result = product_query.write().split('\n')
			start_date = self.numerical_dates[0] if len(self.numerical_dates) > 0 else '20170225'

			
			result = "Il y a eu %i ventes exceptionnelles " %(len(query_result)-1) if len(query_result)-1 < 3 else "Voici les 3 meilleures ventes exceptionnelles "
			result += "du %s au 20170304 " %(start_date)
			result += "pour " + ', '.join(produit_selected) + " " if len(produit_selected) > 0 else ''
			result += "dans les boutiques de " + ', '.join([b for b in self.cities]) + " " if len(self.cities) > 0 else ''
			result += "dans le pays " + ", ".join([p for p in self.countries]) + " " if len(self.cities) == 0 and len(self.countries) > 0 else ''
			result += "\n"
			
			for n, ligne in enumerate(query_result):
				if n > 0:
					colonnes = ligne.split('|')
					item_desc, item_prix, item_date, item_lieu = colonnes
					result += "%s vendu à %s le %s à %s\n" % (item_desc, item_prix, item_date, item_lieu)
			
			print("***************")
			return [product_query.request, result]

		elif margin_query:
			query_result = product_query.write().split('\n')

			print("*** MARGIN")
			print(query_result)
			print("*** DETAILS")
			
			somme = 0
			details_items = []
			for n, ligne in enumerate(query_result):
				if n > 0:
					colonnes = ligne.split('|')
					nombre_ventes = colonnes[1]
					somme += float(nombre_ventes)
				if n > 0 and n < 10:
					details_items.append(colonnes)
				if n == 10:
					details_items.append("...")
					break
			print(details_items)

			return [product_query.request, result, details_items] 
		
		elif croissance_query:
			second_query = copy(product_query)
			if len(self.numerical_dates) > 1:
				product_query.wheredate(sale, 'DateNumYYYYMMDD', self.numerical_dates[0])
				second_query.wheredate(sale, 'DateNumYYYYMMDD', self.numerical_dates[1], self.numerical_dates[0])
			else:
				product_query.wheredate(sale, 'DateNumYYYYMMDD') # par défaut sur les 7 derniers jours
				second_query.wheredate(sale, 'DateNumYYYYMMDD', "20170218", "20170225") # TODO : à changer
			vente_date_n = product_query.write().split('\n')[1]
			vente_date_n_moins_un = second_query.write().split('\n')[1]
			
			if vente_date_n_moins_un == "NULL" or vente_date_n == "NULL":
				result = "Aucune vente enregistrée "
			else:
				vente_date_n = float(vente_date_n)
				vente_date_n_moins_un = float(vente_date_n_moins_un)
				croissance = 100 * (vente_date_n - vente_date_n_moins_un) / vente_date_n_moins_un if vente_date_n_moins_un > 0 else 0
				print("Croissance calculée, ", croissance)
				result = "La croissance est de %i pourcent " %(croissance)

			start_date = self.numerical_dates[0] if len(self.numerical_dates) > 0 else '20170225'
			second_start_date = self.numerical_dates[1] if len(self.numerical_dates) > 1 else '20170218'

			result += "du %s au %s par rapport au %s au %s " %(start_date, "20170304", second_start_date, start_date)
			result += "pour " + ', '.join(produit_selected) + " " if len(produit_selected) > 0 else ''
			result += "dans les boutiques de " + ', '.join([b for b in self.cities]) + " " if len(self.cities) > 0 else ''
			result += "dans le pays " + ", ".join([p for p in self.countries]) + " " if len(self.cities) == 0 and len(self.countries) > 0 else ''

			print("***************")
			return [product_query.request, result]
		
		else:
			product_query.groupby(column_groupby[0], column_groupby[1])
			query_result = product_query.write().split('\n')
			
			somme = 0
			details_items = []
			for n, ligne in enumerate(query_result):
				if n > 0:
					colonnes = ligne.split('|')
					nombre_ventes = colonnes[1]
					somme += float(nombre_ventes)
				if n > 0 and n < 10:
					details_items.append(colonnes)
				if n == 10:
					details_items.append("...")
					break
			print(details_items)
			
			start_date = self.numerical_dates[0] if len(self.numerical_dates) > 0 else '20170225'
			
			result = "Il y a eu " + str(somme) + " ventes en lien avec " + " et/ou ".join(produit_selected) + " "
			result += MDorFP
			result += "du " + start_date + " au " + "20170304 " 
			result += "dans les boutiques de " + ', '.join([b for b in self.cities]) + " " if len(self.cities) > 0 else ''
			result += "dans le pays " + ", ".join([p for p in self.countries]) + " " if len(self.cities) == 0 and len(self.countries) > 0 else ''
			
			print("***************")
			return [product_query.request, result, details_items]

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