import os
import io
import re
import json
import time
import uuid
import difflib
# import torch
import configparser
import traceback
import pandas as pd
from django.http import HttpResponse
from django.http import JsonResponse
from django.http import HttpResponseBadRequest
from django.shortcuts import render
from io import BytesIO
from elasticsearch import Elasticsearch
from ru.utils.common import *
# from sentence_transformers import SentenceTransformer, util

cf = configparser.ConfigParser()
cf.read('ru/config/ru.cfg')

# get Elasticsearch ins
profile = os.environ.get('env', 'develop')
if profile == 'product':
    server_address = '10.166.152.49'
else:
    server_address = 'localhost'
es_ctrl = Elasticsearch([{'host': server_address, 'port': 9200}])


# get info source vectors
# def is_json(text):
#     try:
#         json.loads(text)
#     except ValueError as e:
#         return False
#     return True
#
#
# def apply_parse_json(df):
#     if is_json(df['value'].replace('\\', '')):
#         df['value'] = json.loads(df['value'].replace('\\', ''))
#     return df
#
#
# text_embedding_ins = SentenceTransformer('paraphrase-distilroberta-base-v1', device='cuda')
# info_source_vectors_keywords = []
# datas = es_ctrl.search(index=cf['BABEL']['ES_INDEX_DATAS'], size=200)['hits']['hits']
# if len(datas) > 0:
#     for data in datas:
#         str_result = data['_source']['content']
#         ids = re.findall('\"id\": \"atom(.*?)\"', str_result)
#         names = re.findall('\"name\": \"(.*?)\"', str_result)
#         keywords = re.findall('\"keywords\": \"(.*?)\"', str_result)
#
#         value = re.findall('\"value\": \"(\[.*?\])\"', str_result)
#         if len(value) != len(ids):
#             value = re.findall('\"value\": \"(.*?)\"', str_result)
#
#         vectors_keywords = pd.DataFrame(zip(ids, names, keywords, value), columns=['id', 'name', 'keywords', 'value'])
#         vectors_keywords = vectors_keywords.apply(apply_parse_json, axis=1)
#         vectors_keywords['id'] = 'atom' + vectors_keywords['id']
#         vectors_keywords['vectors'] = pd.Series(list(text_embedding_ins.encode(list(vectors_keywords.keywords.values))))
#         info_source_vectors_keywords.append({'id': data['_source']['data_source_name'], 'data': vectors_keywords})

#elasticdump --input=http://10.166.152.49:9200/pages --output=http://10.166.152.49:9201/pages  --type=data