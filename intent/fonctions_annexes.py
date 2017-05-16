from sql.tables import item, sale, boutique, country, division, retail, theme, department, zone, uzone, sub_zone, family
from intent.mise_en_forme import affichage_euros, affichage_date
from intent.gestion_dates import today, last_monday

def what_products(list_of_dict):
	"""
	Prend self.items en argument, qui est une liste de dictionnaires
	Renvoit une liste de de quadruplets (table, colonne, nom_table, nom_produit)
	"""
	if list_of_dict == []:
		return []

	assert type(list_of_dict) is list, "Expected a list"
	assert type(list_of_dict[0]) is dict, "Expected the list to contain dict"

	products_requested = []
	for produit in list_of_dict :
		for produit_key in produit:
			if produit_key == "division":
				products_requested.append((division, "Description", "Division", produit[produit_key]), "division")
			elif produit_key == "departement":
				products_requested.append((department, "Description", "Department", produit[produit_key]), "departement")
			elif produit_key == "groupe":
				products_requested.append((retail, "Description", "Group", produit[produit_key]), "groupe retail")
			elif produit_key == "theme":
				products_requested.append((theme, "Description", "Theme", produit[produit_key]), "theme")
			elif produit_key == "produit":
				products_requested.append((item, "Description", "Style", produit[produit_key]), "style")
			elif produit_key == "famille":
				products_requested.append((family, "Description", "Family", produit[produit_key]), "famille")
			else:
				print("Erreur, un item n'a pas de catégorie connue !")
	return products_requested

def query_products(list_of_dict):
	products_requested = what_products(list_of_dict)
	has_been_seen = {}
	columns_products = []
	for table, column, table_name, product_name, table_desc in products_requested:
		if not (table_name in has_been_seen and has_been_seen[table_name]):
			columns_products.append((table, column))
			has_been_seen[table_name] = True
	return columns_products

def sale_join_products(query, list_of_dict, main_table = sale):
	print("JOINING PRODUCTS")
	print("================")
	products_requested = what_products(list_of_dict)
	has_been_seen = {}
	for table, column, table_name, product_name, table_desc in products_requested:
		print("Trying to join", table.name)
		if not (table_name in has_been_seen and has_been_seen[table_name]):
			query.join(main_table, table, table_name, "Code")
			print("JOINING", table.name)
			has_been_seen[table_name] = True
	return query

def where_products(query, list_of_dict):
	products_requested = what_products(list_of_dict)
	for table, column, table_name, product_name, table_desc in products_requested:
		query.where(table, column, product_name)
	return query

def find_category(categorie):
	resp = categorie[0:4]
	if resp == "DEPT":
		resp = "Departement"
	elif resp == "DIVI":
		resp = "Division"
	elif resp == "ITEM":
		resp = "Produit"
	elif resp == "GROU":
		resp = "Groupe Retail"
	elif resp == "FAMI":
		resp = "Famille"
	elif resp == "THEM":
		resp = "Theme"
	elif resp == "MOD_":
		resp = "Modele"
	return resp

def append_details_date(details, numerical_dates):
	start_date = numerical_dates[0][0] if len(numerical_dates) > 0 else last_monday()
	end_date = numerical_dates[0][1] if len(numerical_dates) > 0 else today()
	dateFormat = "%Y%m%d"
	a = datetime.strptime(start_date, dateFormat)
	b = datetime.strptime(end_date, dateFormat)
	delta = b - a
	days_diff = delta.days
	print("Days difference: "+days_diff)
	if days_diff>1:
		details.append(["Du", affichage_date(start_date)])
		details.append(["Au (non inclu)", affichage_date(end_date)])
	else:
		details.append(["Le", affichage_date(start_date)])
	return details

def append_details_products(details, items):
	products_requested = what_products(items)
	for table, column, table_name, product_name, table_desc in products_requested:
		details.append([product_name + " trouvé dans", table_desc])
	return details

def append_details_geo(details, geo):
	for geo_zone, geo_item in geo:
		details.append([geo_zone, geo_item])
	return details



"""
Xavier écris en dessous
"""

def geography_joins(table, query, data):

	# GEOGRAPHY Extraction

	uzone_joined = False
	zone_joined = False
	subzone_joined = False
	country_joined = False
	state_joined = False

	query.join(table, zone, "Zone", "Code")

	for geo_table,geo_item in data:
		if geo_table == "uzone" and not uzone_joined:
			query.join(zone, uzone, "uzone", "Code")
			uzone_joined = True
		elif geo_table == "zone" and not zone_joined:
			zone_joined = True
		elif geo_table == "subzone" and not subzone_joined:
			query.join(zone, sub_zone, "Code", "Zone")
			subzone_joined = True
		elif geo_table == "country" and not country_joined:
			query.join(sale, country, "Country", "Code")
			country_joined = True

	return query

def geography_select(query, data):
	for geo_table,geo_item in data:
		if geo_table == "uzone":
			query.where(uzone, "description_FR", geo_item)
		elif geo_table == "zone":
			query.where(zone, "Description", geo_item)
		elif geo_table == "subzone":
			query.where(subzone, "Description", geo_item)
		elif geo_table == "country":
			query.where(country, "Description_FR", geo_item)
	return query








