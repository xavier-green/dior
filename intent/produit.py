
class Produit(object):

	def __init__(self, data):
		self.cities = data['cities']
		self.countries = data['countries']
		self.nationalities = data['nationalities']
		self.dates = data['dates']
		self.items = data['items']

	def build_query(self):
		// bdd = item_item
		// geo ou date -> vente (sales_sales) / (stock)
		// select COUNT
		// nationalites -> vente
		// item obligatoire
