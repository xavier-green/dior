import sys
sys.path.append('/usr/local/Cellar/python3/3.6.0/Frameworks/Python.framework/Versions/3.6/lib/python3.6/site-packages')

from flask import Flask, render_template
from flask import request, jsonify
from flask import jsonify

import numpy as np

app = Flask(__name__)

import fasttext
model_fasttext_path = 'wiki.fr.bin'
model_fasttext = fasttext.load_model(model_fasttext_path)

@app.route('/<string:sentence>', methods=["GET"])
def vector_get(sentence):
	print("new connection from: "+request.remote_addr)
	sentence = sentence.lower()
	if sentence in model_fasttext.words:
		return jsonify(model_fasttext[sentence])
	return jsonify(np.zeros(model_fasttext.dim).tolist())

@app.route('/', methods=["POST"]) # same but getting the sentence via POST
def vector_post():
	print("new post from: "+request.remote_addr)
	words = request.json.get("words", None)
	vectors = []
	for word in words:
		if word.strip() != "":
			if word in model_fasttext.words:
				vectors.append(model_fasttext[word])
			else:
				vectors.append(np.zeros(model_fasttext.dim).tolist())
		else:
			vectors.append(np.zeros(model_fasttext.dim).tolist())
	return jsonify(vectors)

if __name__ == "__main__":
	app.run(host="0.0.0.0",port=80, threaded=True)