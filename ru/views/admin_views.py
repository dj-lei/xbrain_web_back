from ru.views import *


def register(request):
    try:
        if request.method == 'POST':
            username = request.POST.get(cf['ADMIN']['USERNAME'])
            password = request.POST.get(cf['ADMIN']['PASSWORD'])
            user = es_ctrl.search(index=cf['ADMIN']['ES_INDEX'], body=query_dict('username', username))['hits']['hits']
            if len(user) == 0:
                data = {'username': username, 'password': password, 'authority': 'normal', 'groups': [{'project': 'Common', 'role': 'visitor'}]}
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
                        if (elm['role'] in page['role']) or ('visitor' in page['role']):
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
                role = []
                projects = es_ctrl.search(index=cf['ADMIN']['ES_INDEX_PAGES'])['hits']['hits']
                for project in projects:
                    temp = []
                    temp.append({'l': project['_source']['project'], 'k': 'header', 't': ''})
                    temp.append({'l': '', 'k': 'divider', 't': ''})
                    for page in project['_source']['pages']:
                        if 'visitor' in page['role']:
                            temp.append({'l': page['name'], 'k': 'link', 't': page['href']})
                    if len(temp) > 2:
                        role.append({'project': project['_source']['project'], 'role': 'visitor'})
                        result.extend(temp)
                return JsonResponse({'content': result, 'groups': role})
    except Exception as e:
        traceback.print_exc()

