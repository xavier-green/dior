from flask import Flask
from flask import request, jsonify

print("Importing intent class")
from intent.intent import intentModel
print("Importing geo class")
from extraction.geography import WordClassification
print("Importing date class")
from extraction.date import DateExtractor
print("Importing item class")
from extraction.product import ProductExtractor

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
model_fasttext_path = '/Users/xav/Downloads/wiki.fr/wiki.fr.bin'
model_fasttext = fasttext.load_model(model_fasttext_path)

print("Importing responses")
from response import Response
resp = Response()

print("Importing treetagger")

print("Training model")

intent_model = intentModel(model_fasttext)
intent_model.train(data)
#intent_model.predict("prix ht de la rose des vents")

app = Flask("test")

world = WordClassification(model_fasttext)
datex = DateExtractor()
word = ProductExtractor('data/products.csv')

@app.route('/params/<string:sentence>')
def vector_get(sentence):
    global model_fasttext
    if model_fasttext is None:
        model_fasttext = fasttext.load_model(model_fasttext_path)
    intent_extracted = intent_model.predict(sentence)
    geo_extracted = world.find_similar_words(sentence)
    dates_extracted = datex.extract(sentence)
    items_extracted = word.extract(sentence)
    geo_extracted['dates'] = dates_extracted
    geo_extracted['intent'] = intent_extracted
    geo_extracted['items'] = items_extracted
    ans.make(geo_extracted)
    return resp.make(geo_extracted)
    # return str(geo_extracted) # returns the vector of the first word just to check that the model was used

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