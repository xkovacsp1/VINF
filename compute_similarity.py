from elasticsearch import Elasticsearch
import time
import ijson
import scipy.spatial.distance
INDEX_NAME = 'papers'
client = Elasticsearch([{'host': '192.168.99.100', 'port': 9200}],timeout=30, max_retries=10, retry_on_timeout=True)

def find_document(title):
    script_query = {
        "_source": {"includes": ["abstract_vectorized", "title", "categories", "abstract"]},
        'query': {
            'match': {
                'title': title,
            }
        }
    }
    response = client.search(
        index=INDEX_NAME, body=script_query)
    # return match object with biggest score
    if response["hits"]["hits"][0]["_source"]:
        return response["hits"]["hits"][0]["_source"]
    else:
        return LookupError

def semantic_search_universal_sentence_encoder(abstract_vectorized,title,search_size):
    script_query = {
        "size": search_size+1,# because returns the object, which is later filtered out
        "_source": {"includes": ["title", "categories","abstract"]},
        "query": {
            "script_score": {
                "query": {
                    "match_all": {}
                },
                "script": {
                    "source": "cosineSimilarity(params.query_vector, 'abstract_vectorized') + 1.0",
                    "params": {"query_vector": abstract_vectorized}
                }
            }
        }
    }
    search_start = time.time()
    response = client.search(
        index=INDEX_NAME,
        body=script_query)
    search_time = time.time() - search_start
    return list(filter(lambda x: x['_source']['title'] != title, response["hits"]["hits"]))

def semantic_search_TFIDF(abstract, title, search_size):
    script_query = {
        "size": search_size+1,  # because returns the object, which is later filtered out
        "_source": {"includes": ["title", "categories", "abstract"]},
        "query": {
            "more_like_this": {
                "fields": ["abstract"],
                "like": abstract,
                "min_term_freq": 3,
                "max_query_terms": 50,
                "min_doc_freq": 4
            }
        }
    }
    search_start = time.time()
    response = client.search(
        index=INDEX_NAME,
        body=script_query)
    search_time = time.time() - search_start
    return list(filter(lambda x: x['_source']['title'] != title, response["hits"]["hits"]))
