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
                "abstract": {
                    "type": "dense_vector", "dims" : 512 
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

submitter=None
title=None
journal_ref=None
doi=None
report_no=None
categories=None
license=None
abstract=None
pages=None
figures=None
latest_version_date=None
latest_version=None
list_of_authors=None

create_index()
for prefix, the_type, value in ijson.parse(open('df_json_small_tfidf.json')):

    if(prefix == 'item.submitter'):
        submitter=value      
    if(prefix == 'item.title'):
        title=value   
    if(prefix == 'item.journal-ref'):
       journal_ref=value
    if(prefix == 'item.doi'):
        doi=value   
    if(prefix == 'item.report-no'):
        report_no=value
    if(prefix == 'item.categories'):
        categories=eval(value)
    if(prefix == 'item.license'):
        license=value
    if(prefix == 'item.abstract'):
        abstract=eval(value)
    if(prefix == 'item.pages'):
        if(value):
            pages=int(value)
        else:
            pages='No data'
    if(prefix == 'item.figures'):
        if(value):
            figures=int(value)
        else:
            figures='No data'
    if(prefix == 'item.latest_version_date'):
        latest_version_date=value
    if(prefix == 'item.latest_version'):
        latest_version=value
    if(prefix == 'item.list_of_authors'):
        list_of_authors=eval(value)       
    if(submitter and title and journal_ref  and doi and report_no and categories and license and abstract and pages and  figures and latest_version_date and latest_version and list_of_authors):
        body = {
        "submitter":submitter,
        "title":title,
        "journal_ref":journal_ref,
        "doi":doi,
        "report_no":report_no,
        "categories":categories, # mozno sem dat eval
        "license":license,
        "abstract": abstract,
        "pages":pages,
        "figures":figures,
        "latest_version_date":latest_version_date,
        "latest_version":latest_version,
        "list_of_authors":list_of_authors # mozno sem dat eval
        }
        docs.append(body)
        submitter=None
        title=None
        journal_ref=None
        doi=None
        report_no=None
        categories=None
        license=None
        abstract=None
        pages=None
        figures=None
        latest_version_date=None
        latest_version=None
        list_of_authors=None
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
