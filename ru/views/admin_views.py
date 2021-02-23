from ru.views import *


def register(request):
    try:
        if request.method == 'POST':
            username = request.POST.get(cf['ADMIN']['USERNAME'])
            password = request.POST.get(cf['ADMIN']['PASSWORD'])
            user = es_ctrl.search(index=cf['ADMIN']['ES_INDEX'], body=query_dict('username', username))['hits']['hits']
            if len(user) == 0:
                cookie = uuid.uuid4()
                data = {'username': username, 'password': password, 'authority': 'normal', 'cookie': cookie, 'groups': [{'project': 'Common', 'role': 'visitor'}]}
                _ = es_ctrl.index(index=cf['ADMIN']['ES_INDEX'], body=data)
                ret = JsonResponse({'content': 'Success', 'groups': data['groups']})
                ret.set_cookie('x-brain.cdlab.cn.ao.ericsson.se', cookie)
                return ret
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

            user = es_ctrl.search(index=cf['ADMIN']['ES_INDEX'], body=query_with([['username', username]]))['hits']['hits'][0]
            if password == user['_source']['password']:
                result = []
                projects = es_ctrl.search(index=cf['ADMIN']['ES_INDEX_PAGES'])['hits']['hits']
                for project in projects:
                    result.append({'l': project['_source']['project'], 'k': 'header', 't': ''})
                    result.append({'l': '', 'k': 'divider', 't': ''})
                    for page in project['_source']['pages']:
                        result.append({'l': page['name'], 'k': 'link', 't': page['href']})

                user['_source']['cookie'] = uuid.uuid4()
                _ = es_ctrl.update(index=cf['ADMIN']['ES_INDEX'], body={'doc': user['_source']}, id=user['_id'])
                ret = JsonResponse({'content': result, 'groups': user['_source']['groups']})
                ret.set_cookie('x-brain.cdlab.cn.ao.ericsson.se', user['_source']['cookie'])
                return ret
            else:
                return HttpResponseBadRequest
        return HttpResponse(404)
    except Exception as e:
        traceback.print_exc()


def logout(request):
    try:
        username = request.GET.get(cf['ADMIN']['USERNAME'])
        user = es_ctrl.search(index=cf['ADMIN']['ES_INDEX'], body=query_with([['username', username]]))['hits']['hits']
        if len(user) > 0:
            user[0]['_source']['cookie'] = ''
            _ = es_ctrl.update(index=cf['ADMIN']['ES_INDEX'], body={'doc': user[0]['_source']}, id=user[0]['_id'])
            ret = JsonResponse({'content': 'Success'})
            return ret
        else:
            return HttpResponseBadRequest
    except Exception as e:
        traceback.print_exc()


def get(request):
    try:
        if request.method == 'GET':
            operate = request.GET.get(cf['ADMIN']['OPERATE'])
            if request.COOKIES.get('x-brain.cdlab.cn.ao.ericsson.se') is not None:
                user = es_ctrl.search(index=cf['ADMIN']['ES_INDEX'], body=query_with([['cookie', request.COOKIES.get('x-brain.cdlab.cn.ao.ericsson.se')]]))['hits']['hits']
                if len(user) > 0:
                    result = []
                    projects = es_ctrl.search(index=cf['ADMIN']['ES_INDEX_PAGES'])['hits']['hits']
                    for project in projects:
                        result.append({'l': project['_source']['project'], 'k': 'header', 't': ''})
                        result.append({'l': '', 'k': 'divider', 't': ''})
                        for page in project['_source']['pages']:
                            result.append({'l': page['name'], 'k': 'link', 't': page['href']})

                    ret = JsonResponse({'content': result, 'groups': user[0]['_source']['groups'], 'username': user[0]['_source']['username']})
                    return ret

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

