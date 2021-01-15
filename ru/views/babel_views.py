from ru.views import *


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
        return HttpResponse(404)
    except Exception as e:
        traceback.print_exc()


def save(request):
    try:
        if request.method == 'POST':
            data = request.POST.get(cf['BABEL']['GET_DATA'])
            operate = request.POST.get(cf['BABEL']['OPERATE'])
            if operate == cf['BABEL']['NEW_ADD']:
                category = request.POST.get(cf['BABEL']['CATEGORY'])
                symbol_name = request.POST.get(cf['BABEL']['SYMBOL_NAME'])
                _ = es_ctrl.index(index=cf['BABEL']['ES_INDEX_SYMBOLS'], body={'symbol_name': symbol_name,
                        'category': category, 'created_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), 'content': data})
                return JsonResponse({'content': 'Success'})
            elif operate == cf['BABEL']['UPDATE']:
                symbol_id = request.POST.get(cf['BABEL']['SYMBOL_ID'])
                res = es_ctrl.get(index=cf['BABEL']['ES_INDEX_SYMBOLS'], id=symbol_id)['_source']
                res['content'] = data
                _ = es_ctrl.update(index=cf['BABEL']['ES_INDEX_SYMBOLS'], body={'doc': res}, id=symbol_id)
                return JsonResponse({'content': 'Success'})
        return HttpResponse(404)
    except Exception as e:
        traceback.print_exc()
