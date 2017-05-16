from sql.tables import item, sale, boutique, country, division, retail, theme, department, zone, uzone, sub_zone, family, color, material, shape

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
				products_requested.append((division, "Description", "Division", produit[produit_key], "division"))
			elif produit_key == "departement":
				products_requested.append((department, "Description", "Department", produit[produit_key], "departement"))
			elif produit_key == "groupe":
				products_requested.append((retail, "Description", "Group", produit[produit_key], "groupe retail"))
			elif produit_key == "theme":
				products_requested.append((theme, "Description", "Theme", produit[produit_key], "theme"))
			elif produit_key == "produit":
				products_requested.append((item, "Description", "Style", produit[produit_key], "style"))
			elif produit_key == "family":
				products_requested.append((family, "Description", "Family", produit[produit_key], "famille"))
			elif produit_key == "color":
				products_requested.append((color, "Description", "Color", produit[produit_key], "couleur"))
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

