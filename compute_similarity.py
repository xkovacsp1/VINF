from elasticsearch import Elasticsearch
import time
INDEX_NAME = 'papers'
SEARCH_SIZE=5
client = Elasticsearch([{'host': '192.168.99.100', 'port': 9200}])

def find_document(title):
    script_query = {
        'query': {
            'match': {
                'title': title,
            }
        }
    }
    response=client.search(index=INDEX_NAME, body=script_query)
    # return match object with biggest score
    return response["hits"]["hits"][0]["_source"]


def semantic_search(abstract_vector):
    script_query = {
        "size": SEARCH_SIZE,
        "_source": {"includes": ["title"]},
        "query": {
            "script_score": {
                "query": {
                    "match_all": {}
                },
                "script": {
                    "source": "cosineSimilarity(params.query_vector, 'abstract') + 1.0",
                    "params": {"query_vector": abstract_vector}
                }
            }
        }
    }
    search_start = time.time()
    response = client.search(
        index=INDEX_NAME,
        body=script_query)
    search_time = time.time() - search_start
    print()
    print("{} total hits.".format(response["hits"]["total"]["value"]))
    print("search time: {:.2f} ms".format(search_time * 1000))
    """  for hit in response["hits"]["hits"]:
        print("id: {}, score: {}".format(hit["_id"], hit["_score"]))
        print(hit["_source"])
        print() """
    return response["hits"]["hits"]
