from ru.views import *


def register(request):
    try:
        if request.method == 'POST':
            username = request.POST.get(cf['ADMIN']['USERNAME'])
            password = request.POST.get(cf['ADMIN']['PASSWORD'])
            user = es_ctrl.search(index=cf['ADMIN']['ES_INDEX'], body=query_dict('username', username))['hits']['hits']
            if len(user) == 0:
                data = {'username': username, 'password': password, 'authority': 'normal', 'groups': [{'project': 'Common', 'role': 'all'}]}
                _ = es_ctrl.index(index=cf['ADMIN']['ES_INDEX'], body=data)
                return JsonResponse({'content': 'Success', 'groups': data['groups']})
            else:
                return HttpResponseBadRequest
        return HttpResponse(404)
    except Exception as e:
        traceback.print_exc()


def login(request):
    try:
        if request.method == 'POST':
            username = request.POST.get(cf['ADMIN']['USERNAME'])
            password = request.POST.get(cf['ADMIN']['PASSWORD'])

            user = es_ctrl.search(index=cf['ADMIN']['ES_INDEX'], body=query_dict('username', username))['hits']['hits'][0]['_source']
            if password == user['password']:
                result = []
                for elm in user['groups']:
                    pages = es_ctrl.search(index=cf['ADMIN']['ES_INDEX_PAGES'], body=query_dict('project', elm['project']))['hits']['hits'][0]['_source']
                    result.append({'l': elm['project'], 'k': 'header', 't': ''})
                    result.append({'l': '', 'k': 'divider', 't': ''})
                    for page in pages['pages']:
                        if (elm['role'] in page['role']) or ('all' in page['role']):
                            result.append({'l': page['name'], 'k': 'link', 't': page['href']})
                return JsonResponse({'content': result, 'groups': user['groups']})
            else:
                return HttpResponseBadRequest
        return HttpResponse(404)
    except Exception as e:
        traceback.print_exc()


def get(request):
    try:
        if request.method == 'GET':
            operate = request.GET.get(cf['ADMIN']['OPERATE'])
            if operate == cf['ADMIN']['GET_COMMON_PAGES']:
                result = []
                pages = es_ctrl.search(index=cf['ADMIN']['ES_INDEX_PAGES'], body=query_dict('project', 'Common'))['hits']['hits'][0]['_source']
                result.append({'l': 'Common', 'k': 'header', 't': ''})
                result.append({'l': '', 'k': 'divider', 't': ''})
                for page in pages['pages']:
                    result.append({'l': page['name'], 'k': 'link', 't': page['href']})
                return JsonResponse({'content': result, 'groups': [{'project': 'Common', 'role': 'all'}]})
    except Exception as e:
        traceback.print_exc()

