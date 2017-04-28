"""
from importlib.machinery import SourceFileLoader

foo = SourceFileLoader("sql.request", "../sql/request.py").load_module()
foo = SourceFileLoader("sql.tables", "../sql/tables.py").load_module()

"""

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

	def build_answer(self):
		response_base = self.build_query()
		print(response_base)
		response_complete = self.append_details(response_base[1])
		details_query = response_base[2] if len(response_base) > 2 else "No details"
		return [response_base[0],response_complete, details_query] 


	def build_query(self):

		location_query = False
		colour_query = False
		price_query = False

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

		if len(self.items) == 0:
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
		else:
			product_query = query(sale, columns_requested)

		product_query.join(sale, item, "Style", "Code")
		product_query.join(sale, boutique, "Location", "Code")

		if len(self.countries) > 0:
			product_query.join(sale, country, "Country", "Code")

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
					product_query.join(sale, item,"Style","Code")
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

		for ville in self.cities :
			product_query.where(boutique, "Description", ville)

		if len(self.cities) == 0:
			for pays in self.countries :
				product_query.where(country, "Description_FR", pays)

		if len(self.boutiques) > 0:
			for _boutique in self.boutiques :
				product_query.where(boutique, "Description", _boutique)

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
					return result_string
				else:
					return [product_query.request,";;".join(result)]
			else:
				return [product_query.request,"Aucune couleur enregistrée pour "+",".join(self.items)]

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

		else:
			product_query.groupby(column_groupby)
			query_result = product_query.write().split('\n')
			
			somme = 0
			n = 0
			details_items = []
			for ligne in query_result:
				if n > 0:
					colonnes = ligne.split('|')
					nombre_ventes = colonnes[1]
					somme += float(nombre_ventes)
				if n > 0 and n < 20:
					details_items.append(colonnes)
				if n == 20:
					details_items.append("...")
				n += 1
			print(details_items)
			
			start_date = self.numerical_dates[0] if len(self.numerical_dates) > 0 else '20170225'
			
			result = "Il y a eu " + query_result[1] + " ventes en lien avec " + " et/ou ".join(produit_selected) + " "
			result += MDorFP
			result += "du " + start_date + " au " + "20170304 " 
			result += "de la boutique de " + ', '.join([b for b in self.cities]) + " " if len(self.cities) > 0 else ''
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