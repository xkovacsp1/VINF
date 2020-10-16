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
remove=False
module_url = "https://tfhub.dev/google/universal-sentence-encoder/4"
model = hub.load(module_url)
print("module %s loaded" % module_url)

id = None
submitter = None
authors = None
title = None
comments = None
journal_ref = None
doi = None
report_no = None
categories = None
license = None
abstract = None
versions = None
update_date = None
authors_parsed = None
pages = None
figures = None
latest_version_date = None
latest_version = None
list_of_authors = None

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


for prefix, the_type, value in ijson.parse(open('papers_medium.json')):
    #beginning of new paper 
    if(prefix == 'item.id'):
        id = value
        remove = False
    if(remove == False):
        if(prefix == 'item.submitter'):
            submitter = value
        if(prefix == 'item.authors'):
            authors = value
        if(prefix == 'item.title'):
            title = value
        if(prefix == 'item.comments'):
            pages = get_page_number(value)
            figures = get_figure_number(value)
        if(prefix == 'item.journal-ref'):
            journal_ref = value
        if(prefix == 'item.doi'):
            doi = value
        if(prefix == 'item.report-no'):
            report_no = value
        if(prefix == 'item.categories'):
            categories = categories_to_list_of_strings(value)
        if(prefix == 'item.license'):
            license = value
        if(prefix == 'item.abstract'):
            # filter out not accepted papers
            if(bool(re.search('[pP]aper.*[wW]ithdrawn|^[Ww]ithdrawn', value))):
                remove = True
                continue
            # vectorize abstract
            abstract = clean_text(value)
            abstract = remove_stopwords(abstract)
            abstract = model([abstract])           # google sentence encoder
            abstract = format_sentence_encoder_result_to_array(abstract)
        if(prefix == 'item.versions'):
            latest_version_date = get_version_date(value)
            latest_version = get_version_number(value)
        if(prefix == 'item.update_date'):
            update_date = value
        if(prefix == 'item.authors_parsed'):
            list_of_authors = get_list_of_authors(value)
        if(id and submitter and title and journal_ref and doi and report_no and categories and license and abstract and update_date
        and pages and figures and latest_version_date and latest_version and list_of_authors):

            body = {
                "id": id,
                "submitter": submitter,
                "title": title,
                "journal_ref": journal_ref,
                "doi": doi,
                "report_no": report_no,
                "categories": categories, 
                "license": license,
                "abstract": abstract,
                "update_date": update_date,
                "pages": pages,
                "figures": figures,
                "latest_version_date": latest_version_date,
                "latest_version": latest_version,
                "list_of_authors": list_of_authors
            }
            id = None
            submitter = None
            title = None
            journal_ref = None
            doi = None
            report_no = None
            categories = None
            license = None
            abstract = None
            update_date = None
            pages = None
            figures = None
            latest_version_date = None
            latest_version = None
            list_of_authors = None
            docs.append(body)

            count += 1
            if count % 1 == 0:
                append_to_json(docs, 'res.json')
                docs = []
                print("saved {} documents.".format(count))


if docs:
    append_to_json(docs, 'res.json')
    docs = []
    print("saved {} documents.".format(count))
