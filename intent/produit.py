
class Produit(object):

	def __init__(self, data):
		self.cities = data['cities']
		self.countries = data['countries']
		self.nationalities = data['nationalities']
		self.dates = data['dates']
		self.items = data['items']

	def build_answer(self):
		response_base = self.build_query()
		response_complete = self.append_details(response_base)
		return response_complete


	def build_query(self):
		# bdd = item_item
		# geo ou date -> vente (sales_sales) / (stock)
		# select COUNT
		# nationalites -> vente
		# item obligatoire
		if len(self.items) == 0:
			return "Veuillez préciser un produit svp"
		return "Ok"

	def append_details(self, text):
		resp = text[:]+";;"
		if (len(self.cities)>0 or len(self.countries)>0):
			resp += "Avec un critère géographique ("
			if len(self.cities)>0:
				resp += ",".join(self.cities)+","
			if len(self.countries)>0:
				resp += ",".join(self.countries)+","
			if resp[-1]==",":
				resp = resp[:-1]
			resp += ");;"
		if len(self.nationalities)>0:
			resp += "Avec un critère de nationalité ("+",".join(self.nationalities)
			if resp[-1]==",":
				resp = resp[:-1]
			resp += ");;"
		if len(self.dates)>0:
			resp += "Avec un critère de date ("+",".join(self.dates)
			if resp[-1]==",":
				resp = resp[:-1]
			resp += ");;"
		return resp
