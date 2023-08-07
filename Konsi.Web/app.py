from flask import Flask, render_template, request
from elasticsearch import Elasticsearch
from config import *

app = Flask(__name__)

elasticsearch_url = 'http://{}:{}'.format(HOST_ELASTICSEARCH, 9200)

es = Elasticsearch(elasticsearch_url)


@app.route('/')
def index():
    if not es.indices.exists(index=INDEX_ELASTICSEARCH):
        index_body = {
            "mappings": {
                "properties": {
                    "matriculas": {"type": "text"}
                }
            }
        }

        response = es.indices.create(index=INDEX_ELASTICSEARCH, body=index_body)

    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search():
    search_term = request.form['search_term']
    result = search_in_elasticsearch(search_term)
    return render_template('result.html', result=result)


def search_in_elasticsearch(search_term):
    query_body = {
        "query": {
            "match": {
                "matriculas": search_term
            }
        }
    }

    if len(search_term) == 0:
        query_body = None

    result = es.search(index=INDEX_ELASTICSEARCH, body=query_body)

    hits = result['hits']['hits']
    formatted_result = [{'id': hit['_id'], 'content': hit['_source']['matriculas']} for hit in hits]
    return formatted_result


if __name__ == '__main__':
    app.run(debug=True)
