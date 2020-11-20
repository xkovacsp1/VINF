import compute_similarity
import ijson
from nltk.metrics import *
from sklearn.metrics import f1_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
import json

docs=[]
count = 0


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


with open('test_medium.json', 'rb') as data:
    for obj in ijson.items(data, 'item'):
        arr = eval(obj['abstract_vectorized'])
        res = compute_similarity.semantic_search(
            arr, obj['title'],1)
        obj_categories = eval(obj['categories'])
        res_categories = res[0]['_source']['categories']
        #accuracy = accuracy(
            #obj_categories, res_categories)
        #try:
        precision_res = precision(
                set(obj_categories), set(res_categories))
        recall_res = recall(
            set(obj_categories), set(res_categories))
        #except expression as identifier:
            #print(expression)
     
        #obj['accuracy']=accuracy
        obj['precision'] = precision_res
        obj['recall'] = recall_res
        docs.append(obj)
        count += 1
        if count % 10000 == 0:
            append_to_json(docs, 'evaluate_medium.json')
            docs = []
            print("Evaluated {} documents.".format(count))
  
if docs:
    append_to_json(docs, 'evaluate_medium.json')
    docs = []
    print("evaluated {} documents.".format(count))

        


