from annexes.mise_en_forme import affichage_euros, affichage_date
from annexes.gestion_dates import today, last_monday
from annexes.gestion_products import what_products

import datetime

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
	# Parce que la BDD peut avoir des incohérences temporelles
	if start_date[4:] == '0229':
		start_date  = start_date[:4] + '0228'
	if end_date[4:] == '0229':
		end_date  = end_date[:4] + '0228'
	print(end_date)
	a = datetime.datetime.strptime(start_date, dateFormat)
	b = datetime.datetime.strptime(end_date, dateFormat)
	delta = b - a
	days_diff = delta.days
	print("Days difference: "+str(days_diff))
	if days_diff>1:
		end_date_minus = b+datetime.timedelta(days=-1)
		details.append(["Du", affichage_date(start_date)])
		details.append(["Au", affichage_date(end_date_minus.strftime(dateFormat))])
	else:
		details.append(["Le", affichage_date(start_date)])
	return details

def append_details_products(details, items, sources=[]):
	try:
		for index, item in enumerate(items):
			for key in item:
				print("Items trouvés dans la table " + sources[index][0])
				liste_correspondances = [upperfirst(w).rstrip() for w in sources[index][1]]
				details.append([item[key] + " trouvé dans " + sources[index][0], ", ".join(liste_correspondances)])
	except:
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

def upperfirst(x):
	if len(x)>0:
		return x[0].upper() + x[1:].lower()
	return ''

