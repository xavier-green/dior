from sql.tables import item, sale, boutique, country, division, retail, theme, department, zone, uzone, sub_zone, family, color, material, shape, collection

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
			elif produit_key == "famille":
				products_requested.append((family, "Description", "Family", produit[produit_key], "famille"))
			elif produit_key == "color":
				products_requested.append((color, "Description", "Color", produit[produit_key], "couleur"))
			elif produit_key == "material":
				products_requested.append((material, "Description", "Material", produit[produit_key], "materiau"))
			elif produit_key == "shape":
				products_requested.append((shape, "Description", "Shape", produit[produit_key], "shape"))
			elif produit_key == "collection":
				products_requested.append((collection, "Description", "SCS_Collection", produit[produit_key], "collection"))
			else:
				print("Erreur, la catégorie de l'item %s, censée être %s, n'est pas connue !" %(produit[produit_key], produit_key))
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

def sale_join_products(query, list_of_dict, main_table = sale, already_joined = []):
	"""
	Fait les jointures à partir de list_of_dict = self.items
	main_table est censé être soit sale, soit stock
	Les tables Material et Shape ont un traitement spécifique car elles doivent être join sur item
	"""
	products_requested = what_products(list_of_dict)
	has_been_seen = {}
	for table_name in already_joined:
		has_been_seen[table_name] = True

	for table, column, table_name, product_name, table_desc in products_requested:
		print("Trying to join", table.name)
		if not (table_name in has_been_seen and has_been_seen[table_name]):
			if table_name == "Material" or table_name == "Shape":
				if not ("Style" in has_been_seen and has_been_seen["Style"]):
					print("JOINING table ITEM_ITEM pour Material et/ou Shape")
					query.join(main_table, item, "Style", "Code")
					has_been_seen["Style"] = True
				print("JOINING", table.name)
				query.join(item, table, table_name, "Code")

			else:
				query.join(main_table, table, table_name, "Code")
				print("JOINING", table.name)
				has_been_seen[table_name] = True
	return query

def where_products(query, list_of_dict):
	products_requested = what_products(list_of_dict)
	for table, column, table_name, product_name, table_desc in products_requested:
		query.where(table, column, product_name)
	return query

