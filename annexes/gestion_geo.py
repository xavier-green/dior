from sql.tables import item, sale, boutique, country, division, retail, theme, department, zone, uzone, sub_zone, family

"""
def geography_joins(table, query, data):

	# GEOGRAPHY Extraction

	uzone_joined = False
	zone_joined = False
	subzone_joined = False
	country_joined = False
	state_joined = False

	query.join(table, zone, "Zone", "Code")

	for geo_table, geo_item in data:
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
"""

def geography_joins(query, data, already_joined = [], main_table = sale):

	has_been_joined = {
		"uzone": False,
		"zone": False,
		"subzone": False,
		"country": False,
		"state": False
	}

	for table in already_joined:
		if table in has_been_joined:
			has_been_joined[table] = True

	if not has_been_joined["zone"]:
		query.join(main_table, zone, "Zone", "Code")
		has_been_joined["zone"] = True

	for geo_table, geo_item in data:
		if geo_table == "uzone" and not has_been_joined["uzone"]:
			query.join(zone, uzone, "uzone", "Code")
			has_been_joined["uzone"] = True
		elif geo_table == "subzone" and not has_been_joined["subzone"]:
			query.join(zone, sub_zone, "Code", "Zone")
			has_been_joined["subzone"] = True
		elif geo_table == "country" and not has_been_joined["country"]:
			query.join(zone, country, "Code", "Zone")
			has_been_joined["country"] = True

	return query

def geography_select(query, data):
	for geo_table, geo_item in data:
		if geo_table == "uzone":
			query.where(uzone, "description_FR", geo_item)
		elif geo_table == "zone":
			query.where(zone, "Description", geo_item)
		elif geo_table == "subzone":
			query.where(subzone, "Description", geo_item)
		elif geo_table == "country":
			query.where(country, "Description_FR", geo_item)
	return query


