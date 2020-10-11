from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import ijson

client = Elasticsearch([{'host': '192.168.99.100', 'port': 9200}])
es = Elasticsearch([{'host': '192.168.99.100', 'port': 9200}])
docs = []
count = 0

def index_batch(docs):
    requests = []
    for i, doc in enumerate(docs):
        request = doc
        request["_op_type"] = "index"
        request["_index"] = 'papers'
        requests.append(request)
    bulk(client, requests)

for prefix, the_type, value in ijson.parse(open('df_json_small_tfidf.json')):
    if(prefix == 'item.abstract'):
      body = {
          "vector": eval(value)}
      docs.append(body)
      count += 1 
      if count % 100 == 0:
        index_batch(docs)
        docs = []
        print("Indexed {} documents.".format(count))

if docs:
    index_batch(docs)
    print("Indexed {} documents.".format(count))

client.indices.refresh(index='papers')
print("Done indexing.")
