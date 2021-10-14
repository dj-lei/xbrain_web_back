from ru.views import *
import requests
from ru.utils.mind_handle import *


def get(request):
    try:
        if request.method == 'GET':
            operate = request.GET.get(cf['BABEL']['OPERATE'])

            ###################### Babel symbols #######################
            if operate == cf['BABEL']['GET_SYMBOLS_TITLES']:
                res = es_ctrl.search(index=cf['BABEL']['ES_INDEX_SYMBOLS'], size=200)
                data = res['hits']['hits']
                result = []
                symbols = []
                if len(data) > 0:
                    for elm in data:
                        result.append({'id': elm['_id'], 'SymbolName': elm['_source']['symbol_name'], 'Icon': '',
                                       'Category': elm['_source']['category'], 'CreatedTime': elm['_source']['created_time']})
                    tmp = []
                    for elm in data:
                        tmp.append(elm['_source']['category'])
                    tmp = set(tmp)
                    for t in set(tmp):
                        temp = []
                        for elm in data:
                            if t == elm['_source']['category']:
                                temp.append({'id': elm['_id'], 'symbol': elm['_source']['symbol_name']})
                        symbols.append({'title': t, 'symbols': temp})
                return JsonResponse({'content': result, 'symbols': symbols})
            elif operate == cf['BABEL']['GET_SYMBOL']:
                symbol_id = request.GET.get(cf['BABEL']['SYMBOL_ID'])
                res = es_ctrl.get(index=cf['BABEL']['ES_INDEX_SYMBOLS'], id=symbol_id)
                return JsonResponse({'content': res['_source'], 'id': symbol_id})
            elif operate == cf['BABEL']['DELETE_SYMBOL']:
                symbol_id = request.GET.get(cf['BABEL']['SYMBOL_ID'])
                _ = es_ctrl.delete(index=cf['BABEL']['ES_INDEX_SYMBOLS'], id=symbol_id)
                return JsonResponse({'content': 'Success'})

            ###################### Babel viewers #######################
            elif operate == cf['BABEL']['GET_VIEWERS_TITLES']:
                res = es_ctrl.search(index=cf['BABEL']['ES_INDEX_VIEWERS'], size=200)
                data = res['hits']['hits']
                result = []
                if len(data) > 0:
                    for elm in data:
                        result.append({'id': elm['_id'], 'ViewerName': elm['_source']['viewer_name'],
                                       'Group': elm['_source']['group'] if "group" in elm['_source'].keys() else 'unknown', 'CreatedTime': elm['_source']['created_time']})
                return JsonResponse({'content': result})
            elif operate == cf['BABEL']['GET_VIEWER']:
                viewer_id = request.GET.get(cf['BABEL']['VIEWER_ID'])
                res = es_ctrl.get(index=cf['BABEL']['ES_INDEX_VIEWERS'], id=viewer_id)
                return JsonResponse({'content': res['_source'], 'id': viewer_id})
            elif operate == cf['BABEL']['DELETE_VIEWER']:
                viewer_id = request.GET.get(cf['BABEL']['VIEWER_ID'])
                _ = es_ctrl.delete(index=cf['BABEL']['ES_INDEX_VIEWERS'], id=viewer_id)
                return JsonResponse({'content': 'Success'})
            elif operate == cf['BABEL']['GET_TEST_DATA']:
                # content = requests.get(request.GET.get('url'))
                # return JsonResponse(eval(content.content.decode()))
                # test = eval(content.content.decode())['content']
                # temp = base64.b64decode(test[0])
                # temp = json.loads(gzip.decompress(temp).decode())
                # a = dict_retrieval_not_with_children(temp, 'UL_FBG_CB_3_SLV_ID.NUM')
                # return JsonResponse({'content': babel_test_data()[0]})
                return JsonResponse({'content': {'radon_point1': random.randint(0, 10), 'radon_point2': random.randint(5, 20)}})
            elif operate == cf['BABEL']['HARDWARE_ENVIRONMENT_READ_STATUS']:
                # content = requests.get(request.GET.get('url'))
                # return JsonResponse(eval(content.content.decode()))
                return JsonResponse({'content': babel_test_he_status()[0]})
            # elif operate == cf['BABEL']['GET_INTERACTIVE_DATA']:
            #     os.environ['SEED'] = request.GET.get('interactive.layer')
            #     return JsonResponse({'content': 'success'})

            ###################### Babel data #######################
            elif operate == cf['BABEL']['GET_DATAS_TITLES']:
                res = es_ctrl.search(index=cf['BABEL']['ES_INDEX_DATAS'], size=200)
                data = res['hits']['hits']
                result = []
                if len(data) > 0:
                    for elm in data:
                        result.append({'id': elm['_id'], 'DataSourceName': elm['_source']['data_source_name'],
                                       'Category': elm['_source']['category'] if "category" in elm[
                                           '_source'].keys() else 'unknown',
                                       'CreatedTime': elm['_source']['created_time']})
                return JsonResponse({'content': result})
            elif operate == cf['BABEL']['GET_DATAS_ALL']:
                res = es_ctrl.search(index=cf['BABEL']['ES_INDEX_DATAS'], size=200)
                data = res['hits']['hits']
                result = []
                if len(data) > 0:
                    for elm in data:
                        result.append({'id': elm['_source']['data_source_name'], 'name': elm['_source']['data_source_name'],
                                       'children': json.loads(elm['_source']['content'])})
                return JsonResponse({'content': result})
            elif operate == cf['BABEL']['DELETE_DATA']:
                data_id = request.GET.get(cf['BABEL']['DATA_ID'])
                _ = es_ctrl.delete(index=cf['BABEL']['ES_INDEX_DATAS'], id=data_id)
                return JsonResponse({'content': 'Success'})

        return HttpResponse(404)
    except Exception as e:
        traceback.print_exc()


def save(request):
    try:
        if request.method == 'POST':
            data = request.POST.get(cf['BABEL']['GET_DATA'])
            operate = request.POST.get(cf['BABEL']['OPERATE'])
            if operate == cf['BABEL']['SYMBOL_NEW_ADD']:
                category = request.POST.get(cf['BABEL']['CATEGORY'])
                node_data = request.POST.get(cf['BABEL']['NODE_DATA'])
                symbol_name = request.POST.get(cf['BABEL']['SYMBOL_NAME'])
                res = es_ctrl.index(index=cf['BABEL']['ES_INDEX_SYMBOLS'], body={'symbol_name': symbol_name, 'node_data': node_data,
                        'category': category, 'created_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), 'content': data}, id='id' + str(uuid.uuid4()).replace('-', ''))
                return JsonResponse({'content': 'Success', 'symbol_id': res['_id']})
            elif operate == cf['BABEL']['SYMBOL_UPDATE']:
                symbol_id = request.POST.get(cf['BABEL']['SYMBOL_ID'])
                res = es_ctrl.get(index=cf['BABEL']['ES_INDEX_SYMBOLS'], id=symbol_id)['_source']
                if data is None:
                    res['symbol_name'] = request.POST.get(cf['BABEL']['SYMBOL_NAME'])
                    res['category'] = request.POST.get(cf['BABEL']['CATEGORY'])
                else:
                    res['content'] = data
                    res['node_data'] = request.POST.get(cf['BABEL']['NODE_DATA'])
                _ = es_ctrl.update(index=cf['BABEL']['ES_INDEX_SYMBOLS'], body={'doc': res}, id=symbol_id)
                return JsonResponse({'content': 'Success', 'symbol_id': symbol_id})
            elif operate == cf['BABEL']['SYMBOL_RELEASE']:
                symbol_id = request.POST.get(cf['BABEL']['SYMBOL_ID'])
                viewer_name = request.POST.get(cf['BABEL']['VIEWER_NAME'])
                group = request.POST.get(cf['BABEL']['GROUP'])
                _ = es_ctrl.index(index=cf['BABEL']['ES_INDEX_VIEWERS'], body={'viewer_name': viewer_name, 'group': group,
                        'created_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), 'content': symbol_id}, id=symbol_id)
                return JsonResponse({'content': 'Success', 'symbol_id': symbol_id})

            ###################### Babel viewer #######################
            elif operate == cf['BABEL']['VIEWER_NEW_ADD']:
                viewer_name = request.POST.get(cf['BABEL']['VIEWER_NAME'])
                group = request.POST.get(cf['BABEL']['GROUP'])
                res = es_ctrl.index(index=cf['BABEL']['ES_INDEX_VIEWERS'], body={'viewer_name': viewer_name, 'group': group,
                        'created_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), 'content': data})
                return JsonResponse({'content': 'Success', 'viewer_id': res['_id']})
            elif operate == cf['BABEL']['VIEWER_UPDATE']:
                viewer_id = request.POST.get(cf['BABEL']['VIEWER_ID'])
                res = es_ctrl.get(index=cf['BABEL']['ES_INDEX_VIEWERS'], id=viewer_id)['_source']
                if data is None:
                    res['viewer_name'] = request.POST.get(cf['BABEL']['VIEWER_NAME'])
                    res['group'] = request.POST.get(cf['BABEL']['GROUP'])
                else:
                    res['content'] = data
                _ = es_ctrl.update(index=cf['BABEL']['ES_INDEX_VIEWERS'], body={'doc': res}, id=viewer_id)
                return JsonResponse({'content': 'Success', 'viewer_id': viewer_id})
            elif operate == cf['BABEL']['HARDWARE_ENVIRONMENT_SAVE_CONFIG']:
                key = request.POST.get('key')

                # url = request.POST.get('url')
                # data = {'sid':(None, request.POST.get('sid')), 'docid':(None, request.POST.get('docid')),'key':(None, request.POST.get('key')),'addr_map':(None, request.POST.get('address_map'))}
                # res = requests.post(url, files=data)
                # return JsonResponse({'content': json.loads(res.content)})
                return JsonResponse(babel_test_he_data(int(os.getenv('SEED', 1)), key))
            elif operate == cf['BABEL']['POST_INTERACTIVE_DATA']:
                url = request.POST.get('url')
                data = {'sid':(None, request.POST.get('sid')), 'docid':(None, request.POST.get('docid')),'key':(None, request.POST.get('key'))}
                res = requests.post(url, files=data)
                return JsonResponse({'content': res.content})

            ###################### Babel data #######################
            elif operate == cf['BABEL']['DATA_NEW_ADD']:
                data = json.loads(request.FILES.get(cf['BABEL']['FILES']).read())

                data_source_name = request.POST.get(cf['BABEL']['DATA_SOURCE_NAME'])
                category = request.POST.get(cf['BABEL']['CATEGORY'])

                res = es_ctrl.index(index=cf['BABEL']['ES_INDEX_DATAS'],
                                    body={'data_source_name': data_source_name, 'category': category,
                                          'created_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                                          'content': json.dumps(data)})
                return JsonResponse({'content': 'Success', 'data_id': res['_id']})
        return HttpResponse(404)
    except Exception as e:
        traceback.print_exc()
