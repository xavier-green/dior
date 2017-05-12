from sql.tables import division, department, retail, theme, item, family

def what_products(liste_of_dict):
	assert type(list_of_dict) is list, "Expected a list"
	assert type(list_of_dict[0]) is dict, "Expected the list to contain dict"

	products_requested = []
	for produit in self.items :
			for produit_key in produit:
				if produit_key == "division":
					products_requested.append((division, produit[produit_key]))
				elif produit_key == "departement":
					products_requested.append((department, produit[produit_key]))
				elif produit_key == "groupe":
					products_requested.append((retail, produit[produit_key]))
				elif produit_key == "theme":
					products_requested.append((theme, produit[produit_key]))
				elif produit_key == "produit":
					products_requested.append((item, produit[produit_key]))
				elif produit_key == "family":
					products_requested.append((family, produit[produit_key]))


"""
Xavier écris en dessous
"""