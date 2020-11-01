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
    return response["hits"]["hits"][0]["_source"]

def semantic_search(abstract_vectorized,title,search_size):
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
    print()
    print("{} total hits.".format(response["hits"]["total"]["value"]))
    print("search time: {:.2f} ms".format(search_time * 1000))
    # filter out the searched document from result
    return list(filter(lambda x: x['_source']['title'] != title, response["hits"]["hits"]))

def semantic_search_without_elastic(abstract_vectorized, title, search_size):
    scores=[]
    count=0
    with open('res_1m.json', 'rb') as data:
        for obj in ijson.items(data, 'item'):
            if(obj['title']==title):
                continue
            distance = scipy.spatial.distance.cosine(
                abstract_vectorized, eval(obj['abstract_vectorized']))
            scores.append(
                {"title": obj['title'], "categories": obj['categories'], "abstract": obj['abstract'], "distance": 1-distance})
            count += 1
            #if count % 10000 == 0:
                #print("scanned {} documents.".format(count))

    # sort by score and return the first n results
    return sorted(scores, key=lambda i: i['distance'], reverse=True)[:search_size]
    



