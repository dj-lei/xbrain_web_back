from ru.views import *
import requests
from ru.utils.mind_handle import *


def get(request):
    try:
        if request.method == 'GET':
            operate = request.GET.get(cf['BABEL']['OPERATE'])
            if operate == cf['BABEL']['GET_SYMBOLS_TITLES']:
                res = es_ctrl.search(index=cf['BABEL']['ES_INDEX_SYMBOLS'])
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
            elif operate == cf['BABEL']['GET_VIEWERS_TITLES']:
                res = es_ctrl.search(index=cf['BABEL']['ES_INDEX_VIEWERS'])
                data = res['hits']['hits']
                result = []
                if len(data) > 0:
                    for elm in data:
                        result.append({'id': elm['_id'], 'ViewerName': elm['_source']['viewer_name'],
                                       'CreatedTime': elm['_source']['created_time']})
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
                # content = requests.get('http://10.166.152.40/ru/docman/get')
                # return JsonResponse(eval(content.content.decode()))

                # test = eval(content.content.decode())['content']
                # temp = base64.b64decode(test[0])
                # temp = json.loads(gzip.decompress(temp).decode())

                # a = dict_retrieval_not_with_children(temp, 'UL_FBG_CB_3_SLV_ID.NUM')
                return JsonResponse({'content': babel_test_data()[0]})
                # return JsonResponse({'content': temp})
            elif operate == cf['BABEL']['HARDWARE_ENVIRONMENT_READ_STATUS']:
                # content = requests.get('http://10.166.152.40/ru/deviceman/get')
                # return JsonResponse(eval(content.content.decode()))
                return JsonResponse({'content': babel_test_he_status()[0]})
            elif operate == cf['BABEL']['GET_INTERACTIVE_DATA']:
                os.environ['SEED'] = request.GET.get('interactive.layer')
                return JsonResponse({'content': 'success'})
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
                api_url = request.POST.get(cf['BABEL']['API_URL'])
                symbol_name = request.POST.get(cf['BABEL']['SYMBOL_NAME'])
                _ = es_ctrl.index(index=cf['BABEL']['ES_INDEX_SYMBOLS'], body={'symbol_name': symbol_name, 'api_bind_data':api_url,
                        'category': category, 'created_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), 'content': data})
                return JsonResponse({'content': 'Success'})
            elif operate == cf['BABEL']['SYMBOL_UPDATE']:
                symbol_id = request.POST.get(cf['BABEL']['SYMBOL_ID'])
                res = es_ctrl.get(index=cf['BABEL']['ES_INDEX_SYMBOLS'], id=symbol_id)['_source']
                res['content'] = data
                _ = es_ctrl.update(index=cf['BABEL']['ES_INDEX_SYMBOLS'], body={'doc': res}, id=symbol_id)
                return JsonResponse({'content': 'Success'})
            elif operate == cf['BABEL']['SAVE_API_BIND_DATA']:
                symbol_id = request.POST.get(cf['BABEL']['SYMBOL_ID'])
                api_url = request.POST.get(cf['BABEL']['API_URL'])
                res = es_ctrl.get(index=cf['BABEL']['ES_INDEX_SYMBOLS'], id=symbol_id)['_source']
                res['api_bind_data'] = api_url
                _ = es_ctrl.update(index=cf['BABEL']['ES_INDEX_SYMBOLS'], body={'doc': res}, id=symbol_id)
                return JsonResponse({'content': 'Success'})
            elif operate == cf['BABEL']['SAVE_API_VIEWER']:
                viewer_id = request.POST.get(cf['BABEL']['VIEWER_ID'])
                api_url = request.POST.get(cf['BABEL']['API_URL'])
                res = es_ctrl.get(index=cf['BABEL']['ES_INDEX_VIEWERS'], id=viewer_id)['_source']
                res['api_viewer'] = api_url
                _ = es_ctrl.update(index=cf['BABEL']['ES_INDEX_VIEWERS'], body={'doc': res}, id=viewer_id)
                return JsonResponse({'content': 'Success'})
            elif operate == cf['BABEL']['VIEWER_NEW_ADD']:
                viewer_name = request.POST.get(cf['BABEL']['VIEWER_NAME'])
                res = es_ctrl.index(index=cf['BABEL']['ES_INDEX_VIEWERS'], body={'viewer_name': viewer_name,
                        'created_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), 'content': data})
                return JsonResponse({'content': 'Success', 'viewer_id': res['_id']})
            elif operate == cf['BABEL']['VIEWER_UPDATE']:
                viewer_id = request.POST.get(cf['BABEL']['VIEWER_ID'])
                res = es_ctrl.get(index=cf['BABEL']['ES_INDEX_VIEWERS'], id=viewer_id)['_source']
                res['content'] = data
                _ = es_ctrl.update(index=cf['BABEL']['ES_INDEX_VIEWERS'], body={'doc': res}, id=viewer_id)
                return JsonResponse({'content': 'Success', 'viewer_id': viewer_id})
            elif operate == cf['BABEL']['HARDWARE_ENVIRONMENT_SAVE_CONFIG']:
                key = request.POST.get('key')
                # file_dict = request.POST.items()
                # data = {}
                # for (k, v) in file_dict:
                #     data[k] = (None, v)
                #
                # res = requests.post('http://10.166.152.40/ru/docman/value', files=data)
                # return JsonResponse({'content': json.loads(res.content)})
                return JsonResponse({'content': babel_test_he_data(int(os.getenv('SEED', 1)), key)})
        return HttpResponse(404)
    except Exception as e:
        traceback.print_exc()
