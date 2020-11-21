import compute_similarity
import ijson
from nltk.metrics import *
from sklearn.metrics import f1_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
import json

docs=[]
precision_sum_universal_sentence_encoder=0
recall_sum_universal_sentence_encoder=0

precision_sum_TFIDF=0
recall_sum_TFIDF=0

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
        obj_categories = eval(obj['categories'])
        arr = eval(obj['abstract_vectorized'])
        res_universal_sentence_encoder = compute_similarity.semantic_search_universal_sentence_encoder(
            arr, obj['title'],0)
        res_categories_universal_sentence_encoder = res_universal_sentence_encoder[0]['_source']['categories']
        res_TFIDF = compute_similarity.semantic_search_TFIDF(
            obj['abstract'], obj['title'], 0)
        #accuracy_res = accuracy(
            #set(obj_categories),  set(res_categories))

        # google universal sentence encoder
        precision_res_universal_sentence_encoder = precision(
                set(obj_categories), set(res_categories_universal_sentence_encoder))
        recall_res_universal_sentence_encoder = recall(
            set(obj_categories), set(res_categories_universal_sentence_encoder))
        precision_sum_universal_sentence_encoder+=precision_res_universal_sentence_encoder
        recall_sum_universal_sentence_encoder+=recall_res_universal_sentence_encoder

        # TFIDF
        if len(res_TFIDF) > 0:
            res_categories_TFIDF = res_TFIDF[0]['_source']['categories']
            precision_res_TFIDF = precision(
            set(obj_categories), set(res_categories_TFIDF))
            recall_res_TFIDF = recall(
            set(obj_categories), set(res_categories_TFIDF))
            precision_sum_TFIDF += precision_res_TFIDF
            recall_sum_TFIDF += recall_res_TFIDF
            obj['precision_TFIDF'] = str(
                precision_res_TFIDF)
            obj['recall_TFIDF'] = str(
            recall_res_TFIDF)
            obj['score_TFIDF'] = str(
            res_TFIDF[0]['_score'])
            obj['most_similar_title_TFIDF'] = res_TFIDF[0]['_source']['title']
            obj['most_similar_categories_TFIDF'] = res_categories_TFIDF
        # more like this does not retrun result
        else:
            obj['precision_TFIDF'] = str(0)
            obj['recall_TFIDF'] = str(0)
            obj['score_TFIDF'] = str(0)
            obj['most_similar_title_TFIDF'] = ''
            obj['most_similar_categories_TFIDF'] = ''

        
        #obj['accuracy']=accuracy_res
        obj['most_similar_title_universal_sentence_encoder'] = res_universal_sentence_encoder[0]['_source']['title']
        obj['most_similar_categories_universal_sentence_encoder'] = res_categories_universal_sentence_encoder
        obj['id']=str(obj['id'])
        obj['precision_universal_sentence_encoder'] = str(
            precision_res_universal_sentence_encoder)
        obj['recall_universal_sentence_encoder'] = str(
            recall_res_universal_sentence_encoder)
        obj['score_universal_sentence_encoder'] = str(
            res_universal_sentence_encoder[0]['_score'])

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


print("mean precision universal sentence encoder  {}".format(
    precision_sum_universal_sentence_encoder/count))
print("mean recall universal sentence encoder {}".format(
    recall_sum_universal_sentence_encoder/count))
print("---------------------------------------")
print("mean precision TFIDF  {}".format(
    precision_sum_TFIDF/count))
print("mean recall TFIDF {}".format(
    recall_sum_TFIDF/count))


