from annexes.mise_en_forme import affichage_euros, affichage_date
from annexes.gestion_dates import today, last_monday
from annexes.gestion_products import what_products

from datetime

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
	end_date = end_date+datetime.timedelta(days=-1)
	dateFormat = "%Y%m%d"
	a = datetime.datetime.strptime(start_date, dateFormat)
	b = datetime.datetime.strptime(end_date, dateFormat)
	delta = b - a
	days_diff = delta.days
	print("Days difference: "+str(days_diff))
	if days_diff>1:
		details.append(["Du", affichage_date(start_date)])
		details.append(["Au", affichage_date(end_date)])
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

def append_details_boutiques(details, boutiques):
	for boutique in boutiques:
		details.append([boutique + " trouvé dans", "boutique"])
	return details

