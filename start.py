from flask import Flask
from flask import request, jsonify
import datetime

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

print("Importing sql files")
from sql.answer import answer
ans = answer()

print("Importing training data")
from data import intent_data
data = intent_data.intentData.data

print("Importing fasttext model")
import sys
sys.path.append('/usr/local/Cellar/python3/3.6.0/Frameworks/Python.framework/Versions/3.6/lib/python3.6/site-packages')
import fasttext
model_fasttext_path = 'wiki.fr.bin'
model_fasttext = fasttext.load_model(model_fasttext_path)

print("Importing responses")
from response import Response
resp = Response()

print("Importing intents")
from intent.vente import Vente
from intent.vendeur import Vendeur
from intent.stock import Stock

print("Importing treetagger")

print("Training model")

intent_model = intentModel(model_fasttext)
intent_model.train(data)
#intent_model.predict("prix ht de la rose des vents")

app = Flask("test")

world = WordClassification(model_fasttext)
datex = DateExtractor()
word = ProductExtractor('data/products.csv')
bouti = extract_boutique('data/Boutiques.csv')

@app.route('/params/<string:sentence>', methods=["GET"])
def vector_get(sentence):
	print("new connection from: "+request.remote_addr)
	sentence = sentence.lower()
	global model_fasttext
	if model_fasttext is None:
		model_fasttext = fasttext.load_model(model_fasttext_path)
	intent_extracted = intent_model.predict(sentence)
	geo_extracted = world.find_similar_words(sentence)
	dates_extracted = datex.extract(sentence)
	numerical_dates_extracted = datex.extract_numerical(sentence)
	items_extracted = word.extract(sentence)
	geo_extracted['dates'] = dates_extracted
	geo_extracted['numerical_dates'] = numerical_dates_extracted
	geo_extracted['intent'] = intent_extracted
	geo_extracted['items'] = items_extracted
	geo_extracted['sentence'] = sentence
	
	print('data extracted:')
	print(geo_extracted)

	anwser = ""

	if intent_extracted == 'vente':
		print("Detected it's a sale \n")
		produit = Vente(geo_extracted)
		answer = produit.build_answer()
	elif intent_extracted == 'vendeur':
		print("Vous avez demandé des informations au sujet du staff \n")
		vendeur = Vendeur(geo_extracted)
		answer = vendeur.build_answer()
	elif intent_extracted == 'stock':
		print("Vous avez demandé des informations au sujet du stock \n")
		my_stock = Stock(geo_extracted)
		answer = my_stock.build_answer()
	else:
		answer = ["","Bonjour, malheureusement je n'ai pas saisi votre requête. Pouvez-vous reformuler ?"]

	with open("logs.txt", "a") as myfile:
		now = datetime.datetime.now()
		mainString = now.strftime("%Y-%m-%d %H:%M")+"||"+sentence+"||"+answer[0]+"||"+answer[1]
		mainString = mainString.replace('\n','')
		print("logged: "+mainString)
		myfile.write(mainString+"\n")

	return answer[1]

#, ans.make(geo_extracted)
    # return str(geo_extracted) # returns the vector of the first word just to check that the model was used

@app.route('/logs',methods=["GET"])
def get_logs():
	with open("logs.txt") as f:
		content = f.readlines()
		content = [x for x in content]
		print(content)
		center = ""
		for entry in content:
			center += "<tr>"
			words = entry.split("||")
			for word in words:
				center += "<td>"+word+"</td>"
			center += "</tr>"

		return """<!DOCTYPE html>
        <html>
            <head>
                <meta charset="utf-8" />
                <title>Logs</title>
            </head>
        
            <body>
            	<table><th><td>Date</td><td>Requete</td><td>SQL</td><td>Reponse</td></th>
            	{center}
            	</table>
            </body>
        </html>""".format(center=center)

@app.route('/', methods=["POST"]) # same but getting the sentence via POST
def vector_post():
	global model_fasttext
	if request.json is None:
		return "incorrect request (no json attached)"

	sentence = request.json.get("sentence", None)

	if sentence is None:
		return "incorrect request (no sentence field)"
	return str(model_fasttext[sentence.split()[0]])

app.run(host="0.0.0.0")
