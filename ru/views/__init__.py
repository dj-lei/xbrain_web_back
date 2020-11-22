import os
import io
import re
import json
import time
import difflib
import configparser
import traceback
import pandas as pd
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
from elasticsearch import Elasticsearch

cf = configparser.ConfigParser()
cf.read('ru/config/ru.cfg')

# es_ctrl = Elasticsearch([{'host': '10.166.152.49', 'port': 9200}])
es_ctrl = Elasticsearch([{'host': 'localhost', 'port': 9200}])