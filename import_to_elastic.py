from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import ijson
INDEX_NAME='papers'
client = Elasticsearch([{'host': '192.168.99.100', 'port': 9200}])
es = Elasticsearch([{'host': '192.168.99.100', 'port': 9200}])
docs = []
count = 0

def create_index():
    """ Creates an Elasticsearch index."""
    is_created = False
    # Index settings
    settings = {
        "settings": {
            "number_of_shards": 2,
            "number_of_replicas": 1
        },
        "mappings": {
            "dynamic": "true",
            "_source": {
            "enabled": "true"
            },
            "properties": {
                "vector": {
                    "type": "dense_vector", "dims" : 512 
                },
                  "title": {
                    "type": "text"
                }
            }
        }
    }
    print('Creating `papers` index...')
    try:
        if client.indices.exists(INDEX_NAME):
            client.indices.delete(index=INDEX_NAME, ignore=[404])
        client.indices.create(index=INDEX_NAME, body=settings)
        is_created = True
        print('index `papers` created successfully.')
    except Exception as ex:
        print(str(ex))
    finally:
        return is_created
    return is_created

def index_batch(docs):
    requests = []
    for i, doc in enumerate(docs):
        request = doc
        request["_op_type"] = "index"
        request["_index"] = INDEX_NAME
        requests.append(request)
    bulk(client, requests)

title=None
abstract=None
create_index()
for prefix, the_type, value in ijson.parse(open('df_json_small_tfidf.json')):
    if(prefix == 'item.abstract'):
        abstract=eval(value)
    if(prefix == 'item.title'):
        title=value   
    if(title and abstract):

        body = {
        "vector": eval(value),
        "title":title}
        docs.append(body)
        title=None
        abstract=None
        count += 1 
        if count % 100 == 0:
            index_batch(docs)
            docs = []
            print("Indexed {} documents.".format(count))

if docs:
    index_batch(docs)
    print("Indexed {} documents.".format(count))

client.indices.refresh(index=INDEX_NAME)
print("Done indexing.")
