from ru.views import *


def register(request):
    try:
        if request.method == 'POST':
            username = request.POST.get(cf['ADMIN']['USERNAME'])
            password = request.POST.get(cf['ADMIN']['PASSWORD'])
            data = {'username': username, 'password': password, 'authority': 'normal', 'groups': []}
            res = es_ctrl.index(index=cf['ADMIN']['ES_INDEX'], doc_type=cf['ADMIN']['ES_TYPE_ACCOUNT'], body=data)
            return JsonResponse({'groups': []})
        return HttpResponse(404)
    except Exception as e:
        traceback.print_exc()


def login(request):
    try:
        if request.method == 'POST':
            username = request.POST.get(cf['ADMIN']['USERNAME'])
            password = request.POST.get(cf['ADMIN']['PASSWORD'])

            doc = {
                "query": {
                    "term": {
                        'username': str.lower(username)
                    }
                }
            }
            user = es_ctrl.search(index=cf['ADMIN']['ES_INDEX'], doc_type=cf['ADMIN']['ES_TYPE_ACCOUNT'], body=doc)['hits']['hits'][0]['_source']
            if password == user['password']:
                return JsonResponse({'groups': user['groups']})
            else:
                return HttpResponse(500)
        return HttpResponse(404)
    except Exception as e:
        traceback.print_exc()

