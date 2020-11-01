import ijson
import json
import re
import numpy as np
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

docs = []
count = 0
remove = False
module_url = "https://tfhub.dev/google/universal-sentence-encoder/4"
model = hub.load(module_url)
print("module %s loaded" % module_url)

def remove_stopwords(text):
    no_stopword_text = [w for w in text.split() if not w in stop_words]
    return ' '.join(no_stopword_text)

def clean_text(text):
    # remove backslash-apostrophe
    text = re.sub("\'", "", text)
    # remove everything except alphabets and numbers
    text = re.sub("[^a-zA-Z0-9]", " ", text)
    # remove whitespaces
    text = ' '.join(text.split())
    # convert text to lowercase
    text = text.lower()

    return text

def format_sentence_encoder_result_to_array(arr):
    return str(np.array(arr[0]).tolist())

def append_to_json(_dict, path):
    with open(path, 'ab+') as f:
        f.seek(0, 2)  # Go to the end of file
        if f.tell() == 0:  # Check if file is empty
            f.write(json.dumps(_dict).encode())  # If empty, write an array
        else:
            pos = f.seek(-1, 2)
            f.truncate()  # Remove the last character, open the array
            f.write(' , '.encode())  # Write the separator
            # Write after from [ character
            f.write(json.dumps(_dict).encode()[1:])

def get_page_number(str):
    try:
        found = re.search('([0-9]+) +[pP]ages?', str).group(1)
    except AttributeError:
        found = 'No data'
    return found

def get_figure_number(str):
    try:
        found = re.search('([0-9]+) +[fF]igures?', str).group(1)
    except AttributeError:
        found = 'No data'
    return found

def categories_to_list_of_strings(categories):
    return str(categories.split(' '))

def get_version_date(versions):
    versions = eval(versions)
    return str(versions[-1]['created'])

def get_version_number(versions):
    versions = eval(versions)
    return str(versions[-1]['version'])

def get_list_of_authors(authors):
    authors = eval(authors)
    res = list(map(' '.join, authors))
    return str(list(map(str.strip, res)))

with open('papers.json', 'rb') as data:
    for obj in ijson.items(data, 'item'):
        # filter out not accepted papers
        if(bool(re.search('[pP]aper.*[wW]ithdrawn|^[Ww]ithdrawn', obj['abstract']))):
            continue
         # vectorize abstract
        abstract = clean_text(obj['abstract'])
        abstract = remove_stopwords(abstract)
        abstract = model([abstract])           # google sentence encoder
        abstract = format_sentence_encoder_result_to_array(abstract)
        pages = get_page_number(obj['comments'])
        figures = get_figure_number(obj['comments'])
        categories = categories_to_list_of_strings(obj['categories'])
        latest_version_date = get_version_date(obj['versions'])
        latest_version = get_version_number(obj['versions'])
        list_of_authors = get_list_of_authors(obj['authors_parsed'])

        body = {
            "id": obj['id'],
            "submitter": obj['submitter'],
            "title": obj['title'],
            "journal_ref": obj['journal-ref'],
            "doi": obj['doi'],
            "report_no": obj['report-no'],
            "categories": categories,
            "license": obj['license'],
            "abstract": obj['abstract'],
            "abstract_vectorized": abstract,
            "update_date": obj['update_date'],
            "pages": pages,
            "figures": figures,
            "latest_version_date": latest_version_date,
            "latest_version": latest_version,
            "list_of_authors": list_of_authors
        }
        docs.append(body)
        #if count+1 == 1000001:
          #break
        count += 1
        if count % 10000 == 0:
            append_to_json(docs, 'res_1m.json')
            docs = []
            print("saved {} documents.".format(count))

if docs:
    append_to_json(docs, 'res_1m.json')
    docs = []
    print("saved {} documents.".format(count))
