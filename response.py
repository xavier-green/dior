import random

class Response(object):

	bonjour = [
		"Hello! Comment ca va ?",
		"Bonjour :)",
		"Bongiorno !",
		"Salut! Prêt à utiliser DiorBot ?"
	]
	
	def make(self, data):
		intent = data['intent']
		if intent=="bonjour":
			return str(random.choice(self.bonjour))
		else:
			return self.build_custom_answer(data)

	def build_custom_answer(self, data):

		cities = data['cities']
		countries = data['countries']
		nationalities = data['nationalities']
		dates = data['dates']
		intent = data['intent']
		items = data['items']

		resp = "Mmh... Tu as l'air d'avoir envie d'une info sur "
		if intent in ['produit', 'vendeur']:
			resp += 'un '+intent+";;"
		else:
			resp += 'une '+intent+";;"

		if (len(items)>0):
			resp += "Au sujet de produits ("+",".join(items)
			if resp[-1]==",":
				resp = resp[:-1]
			resp += ");;"

		if (len(cities)>0 or len(countries)>0):
			resp += "Avec un critère géographique ("
			if len(cities)>0:
				resp += ",".join(cities)+","
			if len(countries)>0:
				resp += ",".join(countries)+","
			if resp[-1]==",":
				resp = resp[:-1]
			resp += ");;"

		if len(nationalities)>0:
			resp += "Avec un critère de nationalité ("+",".join(nationalities)
			if resp[-1]==",":
				resp = resp[:-1]
			resp += ");;"

		if len(dates)>0:
			resp += "Avec un critère de date ("+",".join(dates)
			if resp[-1]==",":
				resp = resp[:-1]
			resp += ");;"

		return str(resp)







