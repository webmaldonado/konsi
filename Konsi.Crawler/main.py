import requests
import json
import redis
import warnings
import pika
from config import *
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ElasticsearchWarning

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=ElasticsearchWarning)


def obter_token() -> str:
    url = PORTAL_URL_LOGIN

    payload = json.dumps({
        "login": PORTAL_LOGIN,
        "senha": PORTAL_PASSWORD
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    token = response.headers.get('Authorization', '')

    return token


def listar_matriculas(cpf: str):
    url = f"{PORTAL_URL_LISTAGEM}{cpf}"

    payload = {}
    headers = {
        'Authorization': obter_token()
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    content: dict = json.loads(response.content)
    beneficios: list = content.get('beneficios', None)
    return [beneficio['nb'] for beneficio in beneficios if beneficio['nb'] != 'Matrícula não encontrada!']


def salvar_cache(cpf: str, matriculas: list):
    redis_client = redis.StrictRedis(host=HOST_REDIS, port=6379, decode_responses=True)
    matriculas_json = json.dumps(matriculas)
    redis_client.set(cpf, matriculas_json)


def obter_matriculas_cache(cpf: str) -> list:
    redis_client = redis.StrictRedis(host=HOST_REDIS, port=6379, decode_responses=True)
    valor = redis_client.get(cpf)
    if valor is None:
        return []
    else:
        return json.loads(valor)


def salvar_elasticsearch(cpf: str, matriculas: list):
    elasticsearch_url = 'http://{}:{}'.format(HOST_ELASTICSEARCH, 9200)
    es = Elasticsearch(elasticsearch_url)

    index_name = "konsi"

    valor = {
        "matriculas": matriculas
    }

    response = es.index(index=index_name, body=valor, id=cpf)


def obter_elasticsearch(cpf: str) -> list:
    elasticsearch_url = 'http://{}:{}'.format(HOST_ELASTICSEARCH, 9200)
    es = Elasticsearch(elasticsearch_url)

    index_name = "konsi"

    result = es.get(index=index_name, id=cpf)

    print(result)


def processar(cpf: str):
    matriculas: list = obter_matriculas_cache(cpf)

    if len(matriculas) == 0:
        matriculas = listar_matriculas(cpf)
        if len(matriculas) > 0:
            salvar_cache(cpf, matriculas)

    if len(matriculas) > 0:
        salvar_elasticsearch(cpf, matriculas)


def ler_fila():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=HOST_RABBITMQ, connection_attempts=10))

    channel = connection.channel()

    channel.queue_declare(queue='konsi')

    def callback(ch, method, properties, body):
        processar(body)

    channel.basic_consume(queue='konsi', on_message_callback=callback, auto_ack=True)

    channel.start_consuming()


if __name__ == '__main__':
    ler_fila()
