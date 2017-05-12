from flask import Flask, render_template
from flask import request, jsonify
from flask import jsonify

import flask_admin as admin
import datetime

app = Flask(__name__)

print("Importing intent class")
from intent.intent import intentModel
print("Importing geo class")
from extraction.geography import WordClassification
print("Importing date class")
from extraction.date import DateExtractor
print("Importing item class")
from extraction.product import ProductExtractor
print("Importing boutique class")
from extraction.boutique import extract_boutique
print("Importing glossaire")
from extraction.glossaire import translate_with_glossaire

print("Importing training data")
from data import intent_data
data = intent_data.intentData.data

print("Importing fasttext model")
import sys
sys.path.append('/usr/local/Cellar/python3/3.6.0/Frameworks/Python.framework/Versions/3.6/lib/python3.6/site-packages')

print("Importing responses")
from response import Response
resp = Response()

print("Importing intents")
from intent.vente import Vente
from intent.vendeur import Vendeur
from intent.stock import Stock
from intent.boutique import Boutique

print("Importing treetagger")

print("Training model")

intent_model = intentModel()
intent_model.train(data)
#intent_model.predict("prix ht de la rose des vents")

class Logs(admin.BaseView):
	@admin.expose('/')
	def index(self):
		with open("logs.txt") as f:
			content = f.readlines()
			content = [x for x in content]
			print(content)
			# center = ""
			data = []
			for entry in content:
				# center += "<tr>"
				words = entry.split("||")
				data.append(words)
				# for word in words:
				# 	center += "<td style='border: 1px solid #dddddd;'>"+word+"</td>"
				# center += "</tr>"

		return self.render('logs.html', data=data)


app = Flask("test", template_folder='D:/dior/templates')

world = WordClassification()
datex = DateExtractor()
word = ProductExtractor()
bouti = extract_boutique('data/Boutiques.csv')

def process_sentence(sentence,seuil=None):
	copy = sentence[:]
	sentence = sentence.lower()
	sentence = translate_with_glossaire(sentence)
	intent_extracted = intent_model.predict(sentence)
	geo_extracted,sentence = world.find_similar_words(sentence)
	numerical_dates_extracted = datex.extract_numerical(sentence)
	dates_extracted,sentence = datex.extract(sentence)
	boutiques_extracted,sentence = bouti.extract(sentence)
	items_extracted = word.extract(sentence)
	json = {
		'dates': dates_extracted,
		'geo': geo_extracted,
		'numerical_dates': numerical_dates_extracted,
		'intent': intent_extracted,
		'boutiques': boutiques_extracted,
		'sentence': sentence,
		'seuil': seuil,
		'items': items_extracted
	}

	print('data extracted:')
	print(json)

	if intent_extracted == 'vente':
		print("Detected it's a sale \n")
		produit = Vente(json)
		answer = produit.build_answer()
	elif intent_extracted == 'vendeur':
		print("Vous avez demandé des informations au sujet du staff \n")
		vendeur = Vendeur(json)
		answer = vendeur.build_answer()
	elif intent_extracted == 'stock':
		print("Vous avez demandé des informations au sujet du stock \n")
		my_stock = Stock(json)
		answer = my_stock.build_answer()
	elif intent_extracted == 'boutique':
		print("Vous avez demandé des informations au sujet d'une boutique \n")
		boutique = Boutique(json)
		answer = boutique.build_answer()
	else:
		answer = ["","Bonjour, malheureusement je n'ai pas saisi votre requête. Pouvez-vous reformuler ?"]

	with open("logs.txt", "a") as myfile:
		now = datetime.datetime.now()
		mainString = now.strftime("%Y-%m-%d %H:%M")+"||"+copy+"||"+str(answer[0])+"||"+str(answer[1])
		mainString = mainString.replace('\n','')
		myfile.write(mainString+"\n")

	print("This is what is being returned to the App")
	print("+++++++++++++++++++")
	print(answer[1])
	print("+++++++++++++++++++")

	# if len(answer) > 2:
	# 	print(answer[2])
	# 	detail = []
	# 	for liste in answer[2]:
	# 		detail.append('--'.join(liste))
	# 	detail_string = '??'.join(detail)
	# 	print(detail_string)

	resp_detail = []
	if len(answer) > 2 and answer[2] != "No details":
		print("There are details :", answer[2])
		for liste in answer[2]:
			resp_detail.append({
				'item': str(liste[0].rstrip().lstrip()),
				'count': str(liste[1])
			})
	print(resp_detail)

	# return answer[1]+detail_string if len(answer) > 2 else answer[1]
	return jsonify({
		'answer': str(answer[1]),
		'details': resp_detail
	})

@app.route('/params/<string:sentence>', methods=["GET"])
def vector_get(sentence):
	print("new connection from: "+request.remote_addr)
	return process_sentence(sentence)

@app.route('/', methods=["POST"]) # same but getting the sentence via POST
def vector_post():
	sentence = request.json.get("sentence", None)
	seuil = request.json.get("seuil", None)
	return process_sentence(sentence,seuil=seuil)

# Create admin navbar
admin = admin.Admin(name="Dior Admin Page", template_mode='bootstrap3')
admin.add_view(Logs(name="Logs"))
admin.init_app(app)

if __name__ == "__main__":
	app.run(host="0.0.0.0",threaded=True)
