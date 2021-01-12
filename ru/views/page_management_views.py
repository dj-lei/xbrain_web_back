from ru.views import *


def get(request):
    try:
        if request.method == 'GET':
            operate = request.GET.get(cf['PAGES']['OPERATE'])
            if operate == cf['PAGES']['GET_PAGE_TITLES']:
                data = []
                res = es_ctrl.search(index=cf['PAGES']['ES_INDEX'])['hits']['hits']
                for project in res:
                    for page in project['_source']['pages']:
                        data.append({'pagename': page['name'], 'projectname': project['_source']['project'],
                                     'roles': page['role']})
                return JsonResponse({'content': data})
            elif operate == cf['PAGES']['DELETE_PAGE']:
                project_name = request.GET.get(cf['PAGES']['PROJECT_NAME'])
                page_name = request.GET.get(cf['PAGES']['PAGE_NAME'])
                res = es_ctrl.search(index=cf['PAGES']['ES_INDEX'], body={"query": {"match": {"project": project_name}}})['hits']['hits'][0]['_source']
                pages = res['pages']
                # update pages
                for index, page in enumerate(pages):
                    if page['name'] == page_name:
                        pages.pop(index)
                es_ctrl.update_by_query(index=cf['PAGES']['ES_INDEX'],
                                        body={"query": {"match": {"project": project_name}},
                                              "script": {"source": "ctx._source.pages = params.pages",
                                                         "lang": "painless",
                                                         "params": {"pages": pages}}})
                # update admin
                current_role_project = []
                for roles in pages:
                    for role in roles['role']:
                        current_role_project.append(role)
                current_role_project = list(set(current_role_project))
                res_admin = es_ctrl.search(index=cf['ADMIN']['ES_INDEX'], size=100)['hits']['hits']
                flag = 0
                for user in res_admin:
                    if user['_source']['groups']:
                        for group in user['_source']['groups']:
                            if group['project'] == project_name and group['role'] not in current_role_project and group['role'] != 'all':
                                group['role'] = "visitor"
                                flag = 1
                                break
                        if flag:
                            es_ctrl.update(index=cf['ADMIN']['ES_INDEX'], id=user['_id'],
                                           body={"doc": {"groups": user['_source']['groups']}})
                return JsonResponse({'content': 'Success'})
            elif operate == cf['PAGES']['GET_PAGE_ROLES']:
                page_name = request.GET.get(cf['PAGES']['PAGE_NAME'])
                project_name = request.GET.get(cf['PAGES']['PROJECT_NAME'])
                res = es_ctrl.search(index=cf['PAGES']['ES_INDEX'],
                                     body={"query": {"match": {"project": project_name}}})['hits']['hits'][0]['_source']['pages']
                data = []
                roles = []
                for r in res:
                    if r['name'] == page_name:
                        roles = r['role']
                        break
                for i in roles:
                    data.append({'role': i})
                return JsonResponse({'content': data})
    except Exception as e:
        traceback.print_exc()


def save(request):
    try:
        if request.method == 'POST':
            page_name = request.POST.get(cf['PAGES']['PAGE_NAME'])
            project_name = request.POST.get(cf['PAGES']['PROJECT_NAME'])
            role = request.POST.get(cf['PAGES']['ROLE'])
            action = request.POST.get(cf['PAGES']['ACTION'])
            if action == 'Add':
                res = es_ctrl.search(index=cf['PAGES']['ES_INDEX'],
                                     body={"query": {"match": {"project": project_name}}})['hits']['hits'][0]['_source']['pages']
                flag = 0
                for r in res:
                    if r['name'] == page_name:
                        if role not in r['role']:
                            r['role'].append(role)
                            break
                        else:
                            flag = 1
                            break
                if not flag:
                    es_ctrl.update_by_query(index=cf['PAGES']['ES_INDEX'],
                                            body={"query": {"match": {"project": project_name}},
                                                  "script": {"source": "ctx._source.pages = params.pages",
                                                             "lang": "painless",
                                                             "params": {"pages": res}}})
                    data = []
                    roles = []
                    for r in res:
                        if r['name'] == page_name:
                            roles = r['role']
                            break
                    for i in roles:
                        data.append({'role': i})
                    return JsonResponse({'content': 'Success', 'data': data})
                else:
                    return JsonResponse({'content': 'This role has already existed.'})
            elif action == 'Delete':
                res = es_ctrl.search(index=cf['PAGES']['ES_INDEX'],
                                     body={"query": {"match": {"project": project_name}}})['hits']['hits'][0][
                    '_source']['pages']
                for r in res:
                    if r['name'] == page_name:
                        r['role'].remove(role)
                        break
                es_ctrl.update_by_query(index=cf['PAGES']['ES_INDEX'],
                                        body={"query": {"match": {"project": project_name}},
                                              "script": {"source": "ctx._source.pages = params.pages",
                                                         "lang": "painless",
                                                         "params": {"pages": res}}})
                data = []
                roles = []
                for r in res:
                    if r['name'] == page_name:
                        roles = r['role']
                        break
                for i in roles:
                    data.append({'role': i})
                # update admin
                current_role_project = []
                for roles in res:
                    for role in roles['role']:
                        current_role_project.append(role)
                current_role_project = list(set(current_role_project))
                res_admin = es_ctrl.search(index=cf['ADMIN']['ES_INDEX'], size=100)['hits']['hits']
                flag = 0
                for user in res_admin:
                    if user['_source']['groups']:
                        for group in user['_source']['groups']:
                            if group['project'] == project_name and group['role'] not in current_role_project and group['role'] != 'all':
                                group['role'] = "visitor"
                                flag = 1
                                break
                        if flag:
                            es_ctrl.update(index=cf['ADMIN']['ES_INDEX'], id=user['_id'],
                                           body={"doc": {"groups": user['_source']['groups']}})
                return JsonResponse({"content": "Success", 'data': data})
            return HttpResponse(404)
    except Exception as e:
        traceback.print_exc()
