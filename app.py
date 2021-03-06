from flask import Flask, request
import logging
import json
import compute_similarity
from flask_cors import CORS, cross_origin
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route('/find-similar-documents', methods=['POST'])
@cross_origin()
def find_similar_documents_handler():
    try:
        reqBody = request.get_json()
        # Find vectorized abstract for a given title with ElasticSearch
        res = compute_similarity.find_document(reqBody['title'])
        # Retrieve the semantically similar documents for the abstract
        documents = compute_similarity.semantic_search_universal_sentence_encoder(
            res['abstract_vectorized'], res['title'], reqBody['number_of_similar_documents']) if reqBody['use_universal_sentence_encoder'] else compute_similarity.semantic_search_TFIDF(
            res['abstract'], res['title'], reqBody['number_of_similar_documents'])
        return {"searched_document": {'title': res['title'],
                                      'abstract': res['abstract'], 'categories': res['categories']}, "similar_documents": documents}, 200
    except NameError:
        return "invalid request", 400
    except ValueError:
        return "invalid request", 400
    except KeyError:
        return "invalid key in request", 400
    except LookupError :
        return "no result for searched term", 400
