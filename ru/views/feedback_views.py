from ru.views import *


def save(request):
    try:
        if request.method == 'POST':
            feedback_id = request.POST.get(cf['FEEDBACK']['FEEDBACK_ID'])
            content = json.loads(request.POST.get(cf['FEEDBACK']['CONTENT']))
            username = request.POST.get(cf['ADMIN']['USERNAME'])
            theme = request.POST.get(cf['FEEDBACK']['THEME'])
            path = request.POST.get(cf['FEEDBACK']['PATH'])
            feedback_type = request.POST.get(cf['FEEDBACK']['TYPE'])

            if feedback_id == '':
                _ = es_ctrl.index(index=cf['FEEDBACK']['ES_INDEX'], body={'username': username, 'theme': theme,
                                                                        'path': path, 'type': feedback_type, 'status': 'active',
                                                                        'created_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), 'content': content})
            else:
                res = es_ctrl.get(index=cf['FEEDBACK']['ES_INDEX'], id=feedback_id)
                res['_source']['content'] = content

                _ = es_ctrl.update(index=cf['FEEDBACK']['ES_INDEX'], body={'doc': res['_source']}, id=feedback_id)
            return JsonResponse({'content': 'Success'})
        return HttpResponse(404)
    except Exception as e:
        traceback.print_exc()


def get(request):
    try:
        if request.method == 'GET':
            operate = request.GET.get(cf['FEEDBACK']['OPERATE'])
            if operate == cf['FEEDBACK']['GET_FEEDBACK_TITLES']:
                res = es_ctrl.search(index=cf['FEEDBACK']['ES_INDEX'])
                data = res['hits']['hits']
                result = []
                if len(data) > 0:
                    for elm in data:
                        result.append({'id': elm['_id'], 'username': elm['_source']['username'],
                                       'Theme': elm['_source']['theme'], 'Path': elm['_source']['path'], 'Status': elm['_source']['status'],
                                       'Type': elm['_source']['type'], 'CreatedTime': elm['_source']['created_time']})
                return JsonResponse({'content': result})
            elif operate == cf['FEEDBACK']['GET_FEEDBACK']:
                feedback_id = request.GET.get(cf['FEEDBACK']['FEEDBACK_ID'])
                res = es_ctrl.get(index=cf['FEEDBACK']['ES_INDEX'], id=feedback_id)
                return JsonResponse({'content': res['_source']['content'], 'id': feedback_id})
            elif operate == cf['FEEDBACK']['FINISH_FEEDBACK']:
                feedback_id = request.GET.get(cf['FEEDBACK']['FEEDBACK_ID'])
                res = es_ctrl.get(index=cf['FEEDBACK']['ES_INDEX'], id=feedback_id)
                res['_source']['status'] = 'finish'
                _ = es_ctrl.update(index=cf['FEEDBACK']['ES_INDEX'], body={'doc': res['_source']}, id=feedback_id)

                return JsonResponse({'content': 'Success'})
    except Exception as e:
        traceback.print_exc()