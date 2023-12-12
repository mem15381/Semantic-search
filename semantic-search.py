from flask import Flask, request, render_template, jsonify
from sentence_transformers import SentenceTransformer, util
import torch
from hazm import *
from jsonformatter import JsonFormatter
from flask_marshmallow import Marshmallow

app = Flask(__name__)
#app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
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
	tagger = POSTagger(model='resources/postagger.model')
	chunker = Chunker(model='resources/chunker.model')
	tagged = tagger.tag(word_tokenize(query))
	print(tagged)
	string1=tree2brackets(chunker.parse(tagged)).split(']')
	queries = []
	for st in string1:
		st = st.replace('[', '')
		st = st.replace(')', '')
		st = st.replace('(', '')
		st = st.replace('، ', '')
		
		if st[:-2] == '،':
		   print(st)
		   st = st[:-1]
		if st.find('NP') != -1:
		   st = st.replace('NP', '')
		   queries.append(st.strip())
		if st.find('VP') != -1:
		   st = st.replace('VP', '')
		   queries.append(st.strip())

	f = open("output_ss.txt", "w")
	w = open("output_tags.txt", "w")
	w.write(query)
	w.write("\n\n====================\n\n")
	top_k = min(5, len(corpus))
	for query in queries:
		
		chunker = Chunker(model='resources/chunker.model')
		tagged = tagger.tag(word_tokenize(query))
		string1=tree2brackets(chunker.parse(tagged)).split(']')
		lst = []
		for st in string1:
			st = st.replace('[', '')
			st = st.replace(')', '')
			st = st.replace('(', '')
			st = st.replace('، ', '')

			if st[:-2] == '،':
			   print(st)
			   st = st[:-1]
			if st.find('NP') != -1:
			   st = st.replace('NP', '')
			   lst.append(st.strip())
			if st.find('VP') != -1:
			   st = st.replace('VP', '')
			   lst.append(st.strip())

		for item in lst:
			query_embedding = embedder.encode(item, convert_to_tensor=True)
		
			# Alternatively, we can also use util.semantic_search to perform cosine similarty + topk
			hits = util.semantic_search(query_embedding, corpus_embeddings, top_k)
			hits = hits[0]      #Get the hits for the first query
			print("\n\n======================\n\n")
			print("Query:", query)
			print("\nTop 15 most similar sentences in corpus:")
			i = 0
			if len(word_tokenize(query)) > 4:
				f.write("\n\n====================\n\n")
				f.write("Query: " + query + "\n")
				for hit in hits:
					if (i < 3):
						print(sentences[hit['corpus_id']], "(Score: {:.4f})".format(hit['score']))
						if (hit['score'] > 0.7): 
							i=i+1
							f.write(sentences[hit['corpus_id']] + "(Score: {:.4f})".format(hit['score']) + "\n")
							if i < 2:
								w.write("#" + sentences[hit['corpus_id']] + "(Score: {:.4f})".format(hit['score']) + "\n")
								
	f.close()
	w.close()
	return  jsonify(result=s)

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