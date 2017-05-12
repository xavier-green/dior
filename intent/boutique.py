"""
from importlib.machinery import SourceFileLoader

foo = SourceFileLoader("sql.request", "../sql/request.py").load_module()
foo = SourceFileLoader("sql.tables", "../sql/tables.py").load_module()

"""

from intent.mise_en_forme import affichage_euros, affichage_date
# sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'sql'))
from sql.request import query

# Import de toutes les tables utilisées
from sql.tables import item, sale, boutique, country, division, retail, theme, department, zone, sub_zone, uzone

class Boutique(object):

	def __init__(self, data):
		self.geo = data['geo']
		# self.nationalities = data['nationalities']
		self.dates = data['dates']
		self.numerical_dates = data['numerical_dates']
		self.items = data['items']
		self.sentence = data['sentence']

	def build_answer(self):
		response_base = self.build_query()
		print(response_base)
		response_complete = response_base[1]

		details_query = response_base[2] if len(response_base) > 2 else "No details"
		return [response_base[0],response_complete, details_query]


	def build_query(self):

		"""
		Creation de la query secondaire pour un join futur
		"""

		sale_table = query(sale, ['*'])

		sale_table.join(sale, zone, 'Zone', 'Code')
		sale_table.whereNotJDAandOTH()

		if len(self.numerical_dates) > 0:
			sale_table.wheredate(sale, 'DateNumYYYYMMDD', self.numerical_dates[0][0], self.numerical_dates[0][1])
		else:
			sale_table.wheredate(sale, 'DateNumYYYYMMDD') # par défaut sur les 7 derniers jours


		"""
		Jointure avec la vraie query
		"""
		# On détermine si la requête porte sur une boutique, un pays, une zone, ...
		if "zone" in self.sentence.lower():
			boutique_query = query(zone, ['Description', 'count(*)', ("sum", sale, "Std_RP_WOTax_REF")], 'TOP 7')
			scale_cible = "zones"
			boutique_query.join_custom(zone, sale_table.request, sale, "Code", "Zone")
		elif "pays" in self.sentence.lower():
			boutique_query = query(country, ['Description', 'count(*)', ("sum", sale, "Std_RP_WOTax_REF")], 'TOP 3')
			scale_cible = "pays"
			boutique_query.join_custom(country, sale_table.request, sale, "Code", "Country")
		else:
			boutique_query = query(boutique, ['Description', 'count(*)', ("sum", sale, "Std_RP_WOTax_REF")], 'TOP 3')
			scale_cible = "boutiques"
			boutique_query.join_custom(boutique, sale_table.request, sale, "Code", "Location")



		"""
		Jointures
		"""

		# GEOGRAPHY Extraction

		uzone_joined = False
		zone_joined = False
		subzone_joined = False
		country_joined = False
		state_joined = False

		boutique_query.join(sale, zone, "Zone", "Code")

		for geo_table,geo_item in self.geo:
			if geo_table == "uzone" and not uzone_joined:
				boutique_query.join(zone, uzone, "uzone", "Code")
				uzone_joined = True
			elif geo_table == "zone" and not zone_joined:
				zone_joined = True
			elif geo_table == "subzone" and not subzone_joined:
				boutique_query.join(zone, sub_zone, "Code", "Zone")
				subzone_joined = True
			elif geo_table == "country" and not country_joined:
				boutique_query.join(sale, country, "Country", "Code")
				country_joined = True

		produit_selected = []
		for produit in self.items :
			for produit_key in produit:
				if produit_key == "division":
					boutique_query.join(sale, division,"Division","Code")
					produit_selected.append("la division " + produit[produit_key])
				elif produit_key == "departement":
					boutique_query.join(sale, department,"Department","Code")
					produit_selected.append("le departement " + produit[produit_key])
				elif produit_key == "groupe":
					boutique_query.join(sale, retail,"Group","Code")
					produit_selected.append("le groupe retail " + produit[produit_key])
				elif produit_key == "theme":
					boutique_query.join(sale, theme,"Theme","Code")
					produit_selected.append("le theme " + produit[produit_key])
				elif produit_key == "produit":
					boutique_query.join(sale, item,"Style","Code")
					produit_selected.append("le produit " + produit[produit_key])

		"""
		Conditions
		"""

		for produit in self.items :
			for produit_key in produit:
				if produit_key == "division":
					boutique_query.where(division, "Description", produit[produit_key])
				elif produit_key == "departement":
					boutique_query.where(department, "Description", produit[produit_key])
				elif produit_key == "groupe":
					boutique_query.where(retail, "Description", produit[produit_key])
				elif produit_key == "theme":
					boutique_query.where(theme, "Description", produit[produit_key])
				elif produit_key == "produit":
					boutique_query.where(item, "Description", produit[produit_key])

		for geo_table,geo_item in self.geo:
			if geo_table == "uzone" and not uzone_joined:
				boutique_query.where(uzone, "description_FR", geo_item)
			elif geo_table == "zone" and not zone_joined:
				boutique_query.where(zone, "Description", geo_item)
			elif geo_table == "subzone" and not subzone_joined:
				boutique_query.where(subzone, "Description", geo_item)
			elif geo_table == "country" and not country_joined:
				boutique_query.where(country, "Description_FR", geo_item)

		"""
		Finitions
		"""

		# On n'oublie pas le GROUP BY, nécessaire ici vu qu'on prend à la fois une colonne et un count(*)
		if scale_cible == 'pays':
			boutique_query.groupby(country, 'Description')
		elif scale_cible == 'zones':
			boutique_query.groupby(zone, 'Description')
		else:
			boutique_query.groupby(boutique, 'Description')

		boutique_query.orderby(None, ('sum', sale, 'Std_RP_WOTax_REF'), " DESC")


		"""
		Traitement de la réponse
		"""

		# La requête est terminée, on utilise le résultat
		result = boutique_query.write()
		print("***************")
		print(result)

		reponse = "Voici les " + scale_cible + " ayant eu les meilleures ventes : \n"

		liste_resultat = result.split("\n")
		for n, ligne in enumerate(liste_resultat):
			if n == 0:
				pass
			else:
				colonnes = ligne.split('#')
				nom = colonnes[0]
				nombre_ventes = colonnes[1]
				montant_ventes = colonnes[2]
				reponse += nom + " avec " + nombre_ventes + " ventes pour un montant de " + affichage_euros(montant_ventes) + " HT ; \n"


		"""
		Ajout des détails
		"""

		start_date = self.numerical_dates[0][0] if len(self.numerical_dates) > 0 else '20170225'
		end_date = self.numerical_dates[0][1] if len(self.numerical_dates) > 0 else '20170304'

		details = []
		details.append(["Du", affichage_date(start_date)])
		details.append(["Au", affichage_date(end_date)])

		if len(self.countries) > 0:
			details.append(["Pays", ", ".join(self.countries)])

		for produit in self.items :
			for key in produit:
				details.append(["%s trouvé dans" %(produit[key]), key])

		print("Details de boutique :", details)

		return [boutique_query.request, reponse, details]

"""
data = {
		'cities' : ['Paris', 'Madrid'],
		'countries' : [],
		'nationalities' : [],
		'dates' : [],
		'numerical_dates' : [],
		'sentence': 'pays',
		'items' : {'produit':['robe']}
		}

test = Boutique(data)
print(test.build_query())
"""
