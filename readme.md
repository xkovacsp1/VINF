# <center>Searching in scientific papers</center>
##  <center>Patrik Kovács</center>
###  <center>Subject: Information retrieval </center>

### How to run
install dependencies - **pip install -r requirements.txt**  
run elasticsearch docker image - **docker run -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" docker.elastic.co/elasticsearch/elasticsearch:7.9.2**  
in order to preprocess dataset run command **python preprocess.py -i inputFileToPreprocess -o preprocessedOutputFile**  
in order to import preprocessed data to elasticsearch run command **python import_to_elastic.py -f fileToImport**  
in order to evaluate software run command **python evaluate.py -i inputFileForEvaluation -o evaluationResultFile**  
in order to run REST service run command  **flask run** 

### Usage of REST service

#### Input
- POST request to url:  **http://127.0.0.1:5000/find-similar-documents**   
- json body:
```json
{
"title":"Plasmon Amplification through Stimulated Emission at Terahertz Frequencies in Graphene",
"use_universal_sentence_encoder":1,
"number_of_similar_documents":1
}
```
#### Output
- returns json body:
```json
{
    "searched_document": {
        "abstract": "  We show that ...",
        "categories": [
            "cond-mat.mes-hall",
            "cond-mat.mtrl-sci"
        ],
        "title": "Plasmon Amplification through Stimulated Emission at Terahertz\n  Frequencies in Graphene"
    },
    "similar_documents": [
        {
            "_id": "4_jiN3YBzHz78cgcANnO",
            "_index": "papers",
            "_score": 1.6729777,
            "_source": {
                "abstract": " We report studies of...",
                "categories": [
                    "cond-mat.mes-hall"
                ],
                "title": "Cyclotron Resonance study of the electron and hole velocity in graphene\n  monolayers"
            },
            "_type": "_doc"
        }
    ]
}
```