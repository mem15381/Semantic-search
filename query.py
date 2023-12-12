from flask import Flask, request, render_template, jsonify
from sentence_transformers import SentenceTransformer, util
import torch
from hazm import *

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
embedder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
with open('sub.txt', encoding="UTF-8") as f:
	corpus = f.read().splitlines()
corpus_embeddings = embedder.encode(corpus, convert_to_tensor=True)

@app.route('/')
def query():
    return render_template('query.html')

@app.route('/', methods=['POST'])

def query_post():
	query = request.form['text']

	top_k = min(20, len(corpus))
	query_embedding = embedder.encode(query, convert_to_tensor=True)

	cos_scores = util.cos_sim(query_embedding, corpus_embeddings)[0]
	top_results = torch.topk(cos_scores, k=top_k)

	print("\n\n======================\n\n")
	print("Query:", query)
	print("\nTop 5 most similar sentences in corpus:")
	s = []
	for score, idx in zip(top_results[0], top_results[1]):
		s.append((corpus[idx] + "(Score: {:.4f})".format(score)))

	return jsonify(result=s)

@app.route('/chunker', methods=['GET'])	
def chunker():
    return render_template('chunker.html')

@app.route('/chunker', methods=['POST'])
def chunker_post():
	paragraph = request.form['text']
	chunker = Chunker(model='resources/chunker.model')
	tagged = tagger.tag(word_tokenize(paragraph))
	s = tree2brackets(chunker.parse(tagged))
	return jsonify(result=s)