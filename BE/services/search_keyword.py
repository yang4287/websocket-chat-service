from elasticsearch import Elasticsearch
import os
from dotenv import load_dotenv

load_dotenv()

es = Elasticsearch(
    [os.environ.get("ELASTICSEARCH_URL")],
    ca_certs="../http_ca.crt",
    basic_auth=(
        os.environ.get("ELASTICSEARCH_USER"),
        os.environ.get("ELASTICSEARCH_PASS"),
    ),
)


def create_index(index_name):
    es.indices.create(index=index_name, ignore=400)


def add_document(index_name, doc):
    es.index(index=index_name, body=doc)


def search(index_name, query):
    return es.search(index=index_name, body=query)
