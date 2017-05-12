from sql.tables import item, sale, boutique, country, division, retail, theme, department, zone, uzone, sub_zone

def what_products(list_of_dict):
	assert type(list_of_dict) is list, "Expected a list"
	assert type(list_of_dict[0]) is dict, "Expected the list to contain dict"

	products_requested = []
	for produit in list_of_dict :
		for produit_key in produit:
			if produit_key == "division":
				products_requested.append((division, "Description", "Division", produit[produit_key]))
			elif produit_key == "departement":
				products_requested.append((department, "Description", "Department", produit[produit_key]))
			elif produit_key == "groupe":
				products_requested.append((retail, "Description", "Group", produit[produit_key]))
			elif produit_key == "theme":
				products_requested.append((theme, "Description", "Theme", produit[produit_key]))
			elif produit_key == "produit":
				products_requested.append((item, "Description", "Style", produit[produit_key]))
			elif produit_key == "family":
				products_requested.append((family, "Description", "Family", produit[produit_key]))
	return products_requested

def query_products(list_of_dict, has_been_seen = {}):
	products_requested = what_products(list_of_dict)
	for table, column, table_name, product_name in products_requested:
		if not has_been_seen[table_name]:
			pass


def sale_join_products(query, list_of_dict, has_been_seen = {}):
	products_requested = what_products(list_of_dict)
	for table, column, table_name, product_name in products_requested:
		if not has_been_seen[table_name]:
			query.join(sale, table, table_name, "Code")
			has_been_seen[table_name] = True
	return query

def where_products(query, list_of_dict):
	products_requested = what_products(list_of_dict)
	for table, column, table_name, product_name in products_requested:
		query.where(table, column, product_name)
	return query




"""
Xavier écris en dessous
"""

def geography_joins(query, data):
	query.join(sale, item, "Style", "Code")

	# GEOGRAPHY Extraction

	uzone_joined = False
	zone_joined = False
	subzone_joined = False
	country_joined = False
	state_joined = False

	query.join(sale, zone, "Zone", "Code")

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








