import ijson
import json
import re
docs = []
count = 0

id=None
submitter=None
authors=None
title=None
comments=None
journal_ref=None
doi=None
report_no=None
categories=None
license=None
abstract=None
versions=None
update_date=None
authors_parsed=None
pages=None
figures=None
latest_version_date=None
latest_version=None
list_of_authors=None


def append_to_json(_dict,path): 
    with open(path, 'ab+') as f:
        f.seek(0,2)                                #Go to the end of file    
        if f.tell() == 0 :                         #Check if file is empty
            f.write(json.dumps(_dict).encode())  #If empty, write an array
        else :
            pos=f.seek(-1,2)           
            f.truncate()                           #Remove the last character, open the array
            f.write(' , '.encode())                #Write the separator
            f.write(json.dumps(_dict).encode()[1:]) # Write after from [ character
      
for prefix, the_type, value in ijson.parse(open('res.json')):
    if(prefix == 'item.id'):
        id=value
    if(prefix == 'item.submitter'):
        submitter=value
    if(prefix == 'item.authors'):
        authors=value            
    if(prefix == 'item.title'):
        title=value
    if(prefix == 'item.comments'):
        comments=value   
    if(prefix == 'item.journal-ref'):
       journal_ref=value
    if(prefix == 'item.doi'):
        doi=value   
    if(prefix == 'item.report-no'):
        report_no=value
    if(prefix == 'item.categories'):
        categories=value
    if(prefix == 'item.license'):
        license=value
    if(prefix == 'item.abstract'):
        abstract=value
    if(prefix == 'item.versions'):
        versions=value
    if(prefix == 'item.update_date'):
        update_date=value
    if(prefix == 'item.authors_parsed'):
        authors_parsed=value
    if(id and submitter and  authors and title  and comments and journal_ref  and doi and report_no and categories and license and abstract  and versions and update_date and authors_parsed):
         #and pages and  figures and latest_version_date and latest_version and list_of_authors):
        body = {
        "id":id,
        "submitter":submitter,
        "authors":authors,
        "title":title,
        "comments":comments,
        "journal_ref":journal_ref,
        "doi":doi,
        "report_no":report_no,
        "categories":categories, # mozno sem dat eval
        "license":license,
        "abstract": abstract,
        "versions":versions,
        "update_date":update_date,
        "authors_parsed":authors_parsed
        #"pages":pages,
        #"figures":figures,
        #"latest_version_date":latest_version_date,
        #"latest_version":latest_version,
        #"list_of_authors":list_of_authors # mozno sem dat eval
        }
        docs.append(body)
        id=None
        submitter=None
        authors=None
        title=None
        comments=None
        journal_ref=None
        doi=None
        report_no=None
        categories=None
        license=None
        abstract=None
        versions=None
        update_date=None
        authors_parsed=None
        pages=None
        figures=None
        latest_version_date=None
        latest_version=None
        list_of_authors=None

        count += 1 
        if count % 10000 == 0:
            append_to_json(docs,'res.json')
            docs = []
            print("saved {} documents.".format(count))


if docs:
   append_to_json(docs,'res.json')
   docs = []
   print("saved {} documents.".format(count))
   
             