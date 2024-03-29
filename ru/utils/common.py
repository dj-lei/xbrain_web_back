import gzip
import base64
import random
import math
import json
import pandas as pd
from PIL import Image
from io import BytesIO
# from Crypto.Cipher import AES
# from Crypto.Random import get_random_bytes
# from Crypto.PublicKey import RSA


def query_dict(key, value):
    doc = {
        "query": {
            "term": {
                key: str.lower(value)
            }
        }
    }
    return doc


def query_with(kv):
    doc = {
            "query": {
                "bool": {
                    "must": []
                }
            }
        }
    for k, v in kv:
        doc["query"]["bool"]["must"].append({"term": {k: v}})
    return doc


def image_to_base64(image_path):
    pic = Image.open(image_path)
    pic = pic.convert('RGB')
    w, h = pic.size
    if w > 800:
        pic = pic.resize((800, int(h / (w / 800))), Image.ANTIALIAS)
    else:
        pic = pic.resize((w, h), Image.ANTIALIAS)
    output_buffer = BytesIO()
    pic.save(output_buffer, format='JPEG', quality=50)
    byte_data = output_buffer.getvalue()
    base64_str = base64.b64encode(byte_data)
    return base64_str.decode()


def base64_to_image(base64_str):
    byte_data = base64.b64decode(base64_str)
    image_data = BytesIO(byte_data)
    return image_data


def file_compress(file):
    return gzip.compress(file)


def file_decompress(file):
    return gzip.decompress(eval(file))


def echarts_test_data(data=[[12, 5], [24, 20], [36, 36], [48, 10], [60, 10], [72, 20]]):
    option = {
        'title': {'text': 'Line Chart'},
        'tooltip': {},
        'toolbox': {
            'feature': {
                'dataView': {},
                'saveAsImage': {
                    'pixelRatio': 2
                },
                'restore': {}
            }
        },
        'xAxis': {},
        'yAxis': {},
        'series': [{
            'type': 'line',
            'smooth': True,
            'data': data
        }]
    }
    return option


def babel_test_data():
    data = pd.read_excel("D:\\projects\\test\\RSW_Monitor.xlsx")
    RSW_Monitor_node = pd.read_excel("D:\\projects\\test\\RSW_Monitor_node.xlsx")

    level = list(RSW_Monitor_node.Level.values)
    rel = {}
    rel_flag = {}
    height = 1000
    width = 200
    width_clearance = 50
    height_clearance = 20
    RSW_Monitor_node['height'] = 0
    RSW_Monitor_node['width'] = width - width_clearance
    RSW_Monitor_node['location_x'] = 0
    RSW_Monitor_node['location_y'] = 0

    for i in set(level):
        rel[str(i)] = level.count(i)
        rel_flag[str(i)] = 0

    for i, level in enumerate(RSW_Monitor_node.Level.values):
        RSW_Monitor_node.loc[i, 'height'] = int(height / rel[str(level)]) - height_clearance
        RSW_Monitor_node.loc[i, 'location_x'] = level * width * 2

        num = rel_flag[str(level)]
        RSW_Monitor_node.loc[i, 'location_y'] = num * int(height / rel[str(level)])
        rel_flag[str(level)] = rel_flag[str(level)] + 1

    nodes = []
    for node,level,height,width,location_x,location_y in RSW_Monitor_node.values:
        nodes.append({'id': node, 'height': height, 'width': width, 'location_x': location_x, 'location_y': location_y})

    links = []
    for rel, source, target in data[['High Speed Link', 'A Side', 'B Side']].values:
        links.append({'source': source, 'target': target, 'type': rel})

    types = list(set(data['High Speed Link'].values))
    return {'nodes': nodes, 'links': links, 'types': types}


# def babel_test_data():
#     data = pd.read_excel("D:\\projects\\test\\RSW_Monitor.xlsx")
#     a_side = list(data['A Side'].values)
#     b_side = list(data['B Side'].values)
#     a_side.extend(b_side)
#     a_side = set(a_side)
#
#     nodes = []
#     for node in a_side:
#         nodes.append({'id': node})
#
#     links = []
#     for rel, source, target in data[['High Speed Link', 'A Side', 'B Side']].values:
#         links.append({'source': source, 'target': target, 'type': rel})
#
#     types = list(set(data['High Speed Link'].values))
#     return {'nodes': nodes, 'links': links, 'types': types}

def babel_test_he_status(): # status: free,holding,ready
    tmp = [
        {'id': 'a', 'name': 'hardware_environment1', 'server': 'http://localhost:8000/ru/babel/save'},
        {'id': 'b', 'name': 'hardware_environment2', 'server': 'http://localhost:8000/ru/babel/save'},
        {'id': 'c', 'name': 'hardware_environment3', 'server': 'http://localhost:8000/ru/babel/save'}
    ],
    return tmp


def babel_test_he_data(seed, key): # status: free,holding,ready
    temp = {}
    for k in key.split(','):
        temp[k] = random.randint(10 ** seed, 9 + 10 ** seed)
    return temp


# def cal_sin():
#     x = float_range(-1, 1, 0.1)
#     y = float_range(-1, 1, 0.1)
#     return math.sin(x * math.pi) * math.sin(y * math.pi)
#
#
# def float_range(i:float, j:float, k=1)->list:
#     xlen=str((len(str(k-int(k)))-2)/10)+"f"
#     # print("xlen=",xlen)
#     lista=[]
#     while i<j:
#         lista.append(format(i, xlen))
#         i+=k
#     return lista
# def new_rsa_keys(bit):
#     key = RSA.generate(bit)
#     private_key = key.export_key()
#     file_out = open("private.pem", "wb")
#     file_out.write(private_key)
#     file_out.close()
#
#     public_key = key.publickey().export_key()
#     file_out = open("receiver.pem", "wb")
#     file_out.write(public_key)
#     file_out.close()


# def rsa_encrypt(text, public_key):
#     content = text.encode("utf-8")
#     ciphertext = rsa.encrypt(content, public_key)
#     return ciphertext
#
#
# def rsa_decrypt(ciphertext, private_key):
#     content = rsa.decrypt(ciphertext, private_key)
#     text = content.decode("utf-8")
#     return text
