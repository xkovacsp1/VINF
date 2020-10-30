from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import ijson
INDEX_NAME = 'papers'
client = Elasticsearch([{'host': '192.168.99.100', 'port': 9200}])
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
                "abstract": {
                    "type": "dense_vector", "dims": 512
                },
                "title": {
                    "type": "text"
                },
                "submitter": {
                    "type": "text"
                },
                "journal_ref": {
                    "type": "text"
                },
                "doi": {
                    "type": "text"
                },
                "report_no": {
                    "type": "text"
                },
                "categories": {
                    "type": "text"
                },
                "license": {
                    "type": "text"
                },
                "pages": {
                    "type": "text"
                },
                "figures": {
                    "type": "text"
                },
                "latest_version_date": {
                    "type": "text"
                },
                "latest_version": {
                    "type": "text"
                },
                "list_of_authors": {
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


create_index()

with open('res_small.json', 'rb') as data:
    for obj in ijson.items(data, 'item'):
        if(obj['pages'] != 'No data'):
            pages = int(obj['pages'])
        else:
            pages = obj['pages']
        if(obj['figures'] != 'No data'):
            figures = int(obj['figures'])
        else:
            figures = obj['figures']
        categories = eval(obj['categories'])
        abstract = eval(obj['abstract'])
        list_of_authors = eval(obj['list_of_authors'])
        body = {
            "submitter": obj['submitter'],
            "title": obj['title'],
            "journal_ref": obj['journal_ref'],
            "doi": obj['doi'],
            "report_no": obj['report_no'],
            "categories": categories,
            "license": obj['license'],
            "abstract": abstract,
            "pages": pages,
            "figures": figures,
            "latest_version_date": obj['latest_version_date'],
            "latest_version": obj['latest_version'],
            "list_of_authors": list_of_authors
        }
        docs.append(body)
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
