import sys
sys.path.append('/usr/local/Cellar/python3/3.6.0/Frameworks/Python.framework/Versions/3.6/lib/python3.6/site-packages')

from flask import Flask, render_template
from flask import request, jsonify
from flask import jsonify

import numpy as np

app = Flask(__name__)

import fasttext
model_fasttext_path = '/Users/xav/Downloads/wiki.fr/wiki.fr.bin'
model_fasttext = fasttext.load_model(model_fasttext_path)

@app.route('/<string:sentence>', methods=["GET"])
def vector_get(sentence):
	print("new connection from: "+request.remote_addr)
	sentence = sentence.lower()
	if sentence in model_fasttext.words:
		return jsonify(model_fasttext[sentence])
	return jsonify(np.zeros(model_fasttext.dim).tolist())

if __name__ == "__main__":
	app.run(host="0.0.0.0",threaded=True)