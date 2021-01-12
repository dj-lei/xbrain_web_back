from ru.views import *


def get(request):
    try:
        if request.method == 'GET':
            operate = request.GET.get(cf['ADMIN']['OPERATE'])
            if operate == cf['ADMIN']['GET_USER_TITLES']:
                res = es_ctrl.search(index=cf['ADMIN']['ES_INDEX'], size=1000)
                data = res['hits']['hits']
                result = []
                for elm in data:
                    result.append({'id': elm['_id'], 'authority': elm['_source']['authority'],
                                   'roles': '', 'username': elm['_source']['username']})
                    for e in elm['_source']['groups']:
                        result[-1]['roles'] = result[-1]['roles'] + e['project'] + '-' + e['role'] + ' '
                    if result[-1]['roles'] == '':
                        result[-1]['roles'] = 'No roles'
                    else:
                        result[-1]['roles'] = result[-1]['roles'][:-1]
                return JsonResponse({'content': result})
            elif operate == cf['ADMIN']['DELETE_USER']:
                user_id = request.GET.get(cf['ADMIN']['USER_ID'])
                res = es_ctrl.delete(index=cf['ADMIN']['ES_INDEX'], id=user_id)
                return JsonResponse({'content': 'Success'})
            elif operate == cf['ADMIN']['get_the_roles']:
                project = request.GET.get(cf['ADMIN']['PROJECT'])
                res = es_ctrl.search(index=cf['ADMIN']['ES_INDEX_PAGES'], body={"query": {"match": {"project": project}}})['hits']['hits'][0]['_source']
                pages = res['pages']
                role = []
                for page in pages:
                    roles = page['role']
                    for r in roles:
                        role.append(r)
                role = list(set(role))
                return JsonResponse({'content': role})
            elif operate == cf['ADMIN']['GET_PROJECTS_ROLES']:
                data = []
                res = es_ctrl.search(index=cf['ADMIN']['ES_INDEX_PAGES'])['hits']['hits']
                for elm in res:
                    role = []
                    for r in elm['_source']['pages']:
                        role = role + r['role']
                    role = list(set(role))
                    data.append({'project': elm['_source']['project'], 'role': role})
                return JsonResponse({'content': data})
        return HttpResponse(404)
    except Exception as e:
        traceback.print_exc()


def save(request):
    try:
        if request.method == 'POST':
            user_id = request.POST.get(cf['ADMIN']['USER_ID'])
            has_role = request.POST.get(cf['ADMIN']['HAS_ROLE'])
            project_name = request.POST.get(cf['ADMIN']['PROJECT'])
            role_name = request.POST.get(cf['ADMIN']['ROLE'])
            action = request.POST.get(cf['ADMIN']['ACTION'])
            # g = request.POST.get(cf['ADMIN']['GROUPS'])
            if action == 'Delete':
                if has_role == 'No roles':
                    return JsonResponse({'content': 'This user has no access to anything!'})
                else:
                    flag = 0
                    groups = has_role.split(' ')
                    for i in groups:
                        temp = i.split('-')
                        if temp[0] == project_name and temp[1] == role_name:
                            groups.remove(i)
                            flag = 1
                            break
                    if flag:
                        group_data = []
                        data = ''
                        if groups and groups != ['']:
                            for i in groups:
                                temp = i.split('-')
                                group = {'role': temp[1], 'project': temp[0]}
                                group_data.append(group)
                            es_ctrl.update(index=cf['ADMIN']['ES_INDEX'], id=user_id, body={"doc": {"groups": group_data}})
                            for i in group_data:
                                data = data + i['project'] + '-' + i['role'] + ' '
                            data = data[:-1]
                        else:
                            es_ctrl.update(index=cf['ADMIN']['ES_INDEX'], id=user_id,
                                           body={"doc": {"groups": []}})
                            data = 'No roles'
                        return JsonResponse({'content': 'Success', 'data': data})
                    else:
                        return JsonResponse({'content': 'This user did not have this access.'})
            elif action == 'Add':
                if has_role == 'No roles':
                    group_data = [{'role': role_name, 'project': project_name}]
                    es_ctrl.update(index=cf['ADMIN']['ES_INDEX'], id=user_id, body={"doc": {"groups": group_data}})
                    data = group_data[0]['project'] + '-' + group_data[0]['role']
                    return JsonResponse({'content': 'Success', 'data': data})
                else:
                    flag = 0
                    groups = has_role.split(' ')
                    for i in groups:
                        temp = i.split('-')
                        if temp[0] == project_name and temp[1] == role_name:
                            flag = 1
                            break
                    if flag:
                        return JsonResponse({'content': 'This user has already had this access.'})
                    else:
                        group_data = []
                        data = ''
                        for i in groups:
                            temp = i.split('-')
                            group = {'role': temp[1], 'project': temp[0]}
                            group_data.append(group)
                        group_data.append({'role': role_name, 'project': project_name})
                        es_ctrl.update(index=cf['ADMIN']['ES_INDEX'], id=user_id, body={"doc": {"groups": group_data}})
                        for i in group_data:
                            data = data + i['project'] + '-' + i['role'] + ' '
                        data = data[:-1]
                        return JsonResponse({'content': 'Success', 'data': data})
    except Exception as e:
        traceback.print_exc()

