import os
import io
import re
import json
import time
import uuid
import difflib
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

cf = configparser.ConfigParser()
cf.read('ru/config/ru.cfg')

profile = os.environ.get('env', 'develop')
if profile == 'product':
    server_address = '10.166.152.49'
else:
    server_address = 'localhost'

es_ctrl = Elasticsearch([{'host': server_address, 'port': 9200}])

#elasticdump --input=http://10.166.152.49:9200/pages --output=http://10.166.152.49:9201/pages  --type=data