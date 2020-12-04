from ru.views import *
from ru.utils.mind_handle import *
from io import BytesIO
from PIL import Image


def get(request):
    try:
        if request.method == 'GET':
            operate = request.GET.get(cf['TROUBLE_SHOOTING']['OPERATE'])
            if operate == cf['TROUBLE_SHOOTING']['GET_TEMPLATE_TITLES']:
                res = es_ctrl.search(index=cf['TROUBLE_SHOOTING']['ES_INDEX_TEMPLATE'])
                data = res['hits']['hits']
                result = []
                for elm in data:
                    result.append({'id': elm['_id'], 'TemplateName': elm['_source']['TemplateName'],
                                   'Date': elm['_source']['Date']})
                return JsonResponse({'content': result})
            elif operate == cf['TROUBLE_SHOOTING']['GET_TEMPLATE']:
                template_id = request.GET.get(cf['TROUBLE_SHOOTING']['TEMPLATE_ID'])
                res = es_ctrl.get(index=cf['TROUBLE_SHOOTING']['ES_INDEX_TEMPLATE'], id=template_id)
                return JsonResponse({'content': res['_source'], 'id': template_id})
            elif operate == cf['TROUBLE_SHOOTING']['DELETE_TEMPLATE']:
                template_id = request.GET.get(cf['TROUBLE_SHOOTING']['TEMPLATE_ID'])
                _ = es_ctrl.delete(index=cf['TROUBLE_SHOOTING']['ES_INDEX_TEMPLATE'], id=template_id)
                return JsonResponse({'content': 'Success'})
            elif operate == cf['TROUBLE_SHOOTING']['GET_TASK_TITLES']:
                res = es_ctrl.search(index=cf['TROUBLE_SHOOTING']['ES_INDEX_TASK'])
                data = res['hits']['hits']
                result = []
                for elm in data:
                    result.append({'id': elm['_id'], 'TaskName': elm['_source']['TemplateName'], 'Status': elm['_source']['Status'],
                                   'Date': elm['_source']['Date']})
                return JsonResponse({'content': result})
            elif operate == cf['TROUBLE_SHOOTING']['GET_TASK']:
                template_id = request.GET.get(cf['TROUBLE_SHOOTING']['TEMPLATE_ID'])
                res = es_ctrl.get(index=cf['TROUBLE_SHOOTING']['ES_INDEX_TASK'], id=template_id)
                return JsonResponse({'content': res['_source'], 'id': template_id})
            elif operate == cf['TROUBLE_SHOOTING']['DELETE_TASK']:
                template_id = request.GET.get(cf['TROUBLE_SHOOTING']['TEMPLATE_ID'])
                _ = es_ctrl.delete(index=cf['TROUBLE_SHOOTING']['ES_INDEX_TASK'], id=template_id)

                _id = es_ctrl.search(index=cf['TROUBLE_SHOOTING']['ES_INDEX_TASK_IMAGES'],
                                     body=query_dict('task_id', template_id))['hits']['hits'][0]['_id']
                _ = es_ctrl.delete(index=cf['TROUBLE_SHOOTING']['ES_INDEX_TASK_IMAGES'], id=_id)

                _id = es_ctrl.search(index=cf['TROUBLE_SHOOTING']['ES_INDEX_TASK_LOGS'],
                                     body=query_dict('task_id', template_id))['hits']['hits'][0]['_id']
                _ = es_ctrl.delete(index=cf['TROUBLE_SHOOTING']['ES_INDEX_TASK_LOGS'], id=_id)

                return JsonResponse({'content': 'Success'})
            elif operate == cf['TROUBLE_SHOOTING']['CLOSE_TASK']:
                template_id = request.GET.get(cf['TROUBLE_SHOOTING']['TEMPLATE_ID'])
                res = es_ctrl.get(index=cf['TROUBLE_SHOOTING']['ES_INDEX_TASK'], id=template_id)['_source']
                res['Status'] = 'close'
                res['Date'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                replace_res = json.dumps(res).replace('#f1c40e', '#2ecc71').replace('active', 'close')
                res = json.loads(replace_res)

                _ = es_ctrl.delete(index=cf['TROUBLE_SHOOTING']['ES_INDEX_TASK'], id=template_id)
                _ = es_ctrl.index(index=cf['TROUBLE_SHOOTING']['ES_INDEX_TASK'], body=res, id=template_id)

                return JsonResponse({'content': 'Success'})
            elif operate == cf['TROUBLE_SHOOTING']['GET_TASK_DETAILS']:
                template_id = request.GET.get(cf['TROUBLE_SHOOTING']['TEMPLATE_ID'])
                node_id = request.GET.get(cf['TROUBLE_SHOOTING']['NODE_ID'])
                res = es_ctrl.get(index=cf['TROUBLE_SHOOTING']['ES_INDEX_TASK'], id=template_id)
                data = mind_get_list(mind_search_id(res['_source']['nodeData'], node_id))
                result = []
                for elm in data:
                    result.append({'id': elm[0], 'Task': elm[1], 'Status': elm[2], 'Executor': elm[3]})
                return JsonResponse({'content': result, 'id': template_id})
            elif operate == cf['TROUBLE_SHOOTING']['GET_TASK_IMAGES']:
                template_id = request.GET.get(cf['TROUBLE_SHOOTING']['TEMPLATE_ID'])
                res = es_ctrl.search(index=cf['TROUBLE_SHOOTING']['ES_INDEX_TASK_IMAGES'], body=query_dict('task_id', template_id))['hits']['hits'][0]['_source']['content']
                result = []
                for elm in res:
                    result.append("data:image/png;base64," + elm['content'])
                return JsonResponse({'content': result})
            elif operate == cf['TROUBLE_SHOOTING']['GET_TASK_LOGS']:
                template_id = request.GET.get(cf['TROUBLE_SHOOTING']['TEMPLATE_ID'])
                res = es_ctrl.search(index=cf['TROUBLE_SHOOTING']['ES_INDEX_TASK_LOGS'], body=query_dict('task_id', template_id))['hits']['hits'][0]['_source']
                response = HttpResponse(file_decompress(res['content']), 'application/txt')
                response['Content-Disposition'] = res['name']
                response['Access-Control-Expose-Headers'] = 'Content-Disposition'
                return response
            elif operate == cf['TROUBLE_SHOOTING']['GET_CHECKLIST_IMAGES']:
                template_id = request.GET.get(cf['TROUBLE_SHOOTING']['TEMPLATE_ID'])
                node_id = request.GET.get(cf['TROUBLE_SHOOTING']['NODE_ID'])
                res = es_ctrl.search(index=cf['TROUBLE_SHOOTING']['ES_INDEX_CHECKLIST_IMAGES'], body=query_with([['task_id', template_id], ['node_id', node_id]]))['hits']['hits']
                result = []
                if len(res) > 0:
                    res = res[0]['_source']['content']
                    for elm in res:
                        result.append("data:image/png;base64," + elm['content'])
                return JsonResponse({'content': result})
            elif operate == cf['TROUBLE_SHOOTING']['GET_CHECKLIST_LOGS']:
                template_id = request.GET.get(cf['TROUBLE_SHOOTING']['TEMPLATE_ID'])
                node_id = request.GET.get(cf['TROUBLE_SHOOTING']['NODE_ID'])
                res = es_ctrl.search(index=cf['TROUBLE_SHOOTING']['ES_INDEX_CHECKLIST_LOGS'], body=query_with([['task_id', template_id], ['node_id', node_id]]))['hits']['hits']
                result = []
                if len(res) > 0:
                    res = res[0]['_source']['content']
                    for elm in res:
                        result.append({'uuid': elm['uuid'], 'name': elm['name'], 'username': elm['username'], 'created_time': elm['created_time']})
                return JsonResponse({'content': result})
            elif operate == cf['TROUBLE_SHOOTING']['GET_CHECKLIST_LOG']:
                template_id = request.GET.get(cf['TROUBLE_SHOOTING']['TEMPLATE_ID'])
                node_id = request.GET.get(cf['TROUBLE_SHOOTING']['NODE_ID'])
                uuid_id = request.GET.get(cf['TROUBLE_SHOOTING']['UUID_ID'])
                res = es_ctrl.search(index=cf['TROUBLE_SHOOTING']['ES_INDEX_CHECKLIST_LOGS'], body=query_with([['task_id', template_id], ['node_id', node_id]]))['hits']['hits'][0]['_source']['content']

                for elm in res:
                    if elm['uuid'] == uuid_id:
                        response = HttpResponse(file_decompress(elm['content']), 'application/txt')
                        response['Content-Disposition'] = elm['name']
                        response['Access-Control-Expose-Headers'] = 'Content-Disposition'
                        return response
                return HttpResponse(404)
            elif operate == cf['TROUBLE_SHOOTING']['GET_CHECKLIST_COMMENTS']:
                template_id = request.GET.get(cf['TROUBLE_SHOOTING']['TEMPLATE_ID'])
                node_id = request.GET.get(cf['TROUBLE_SHOOTING']['NODE_ID'])
                res = es_ctrl.search(index=cf['TROUBLE_SHOOTING']['ES_INDEX_CHECKLIST_COMMENTS'], body=query_with([['task_id', template_id], ['node_id', node_id]]))['hits']['hits']
                result = []
                if len(res) > 0:
                    res = res[0]['_source']['content']
                    for elm in res:
                        result.append({'uuid': elm['uuid'], 'username': elm['username'], 'created_time': elm['created_time'], 'comment': elm['content']})
                return JsonResponse({'content': result})
        return HttpResponse(404)
    except Exception as e:
        traceback.print_exc()


def save(request):
    try:
        if request.method == 'POST':
            data = request.POST.get(cf['TROUBLE_SHOOTING']['GET_DATA'])
            operate = request.POST.get(cf['TROUBLE_SHOOTING']['OPERATE'])
            if operate == cf['TROUBLE_SHOOTING']['NEW_ADD']:
                _ = es_ctrl.index(index=cf['TROUBLE_SHOOTING']['ES_INDEX_TEMPLATE'], body=data)
                return JsonResponse({'content': 'Success'})
            elif operate == cf['TROUBLE_SHOOTING']['UPDATE']:
                template_id = request.POST.get(cf['TROUBLE_SHOOTING']['TEMPLATE_ID'])
                _ = es_ctrl.delete(index=cf['TROUBLE_SHOOTING']['ES_INDEX_TEMPLATE'], id=template_id)
                _ = es_ctrl.index(index=cf['TROUBLE_SHOOTING']['ES_INDEX_TEMPLATE'], body=data, id=template_id)
                return JsonResponse({'content': 'Success'})
            elif operate == cf['TROUBLE_SHOOTING']['UPDATE_TASK']:
                template_id = request.POST.get(cf['TROUBLE_SHOOTING']['TEMPLATE_ID'])
                selected = request.POST.get(cf['TROUBLE_SHOOTING']['SELECT_TASK'])
                username = request.POST.get(cf['TROUBLE_SHOOTING']['USERNAME'])
                res = es_ctrl.get(index=cf['TROUBLE_SHOOTING']['ES_INDEX_TASK'], id=template_id)['_source']
                replace_res = json.dumps(res)
                for select in json.loads(selected):
                    before_node = mind_search_id(res['nodeData'], select['id'])
                    after_node = before_node.copy()
                    after_node['Status'] = 'close'
                    after_node['Executor'] = username
                    after_node['style'] = {'fontWeight': 'bold', 'color': '#2ecc71'}
                    replace_res = replace_res.replace(json.dumps(before_node), json.dumps(after_node))
                result = json.loads(replace_res)
                after_res = mind_color_update(result['nodeData'])
                result['nodeData'] = after_res

                _ = es_ctrl.delete(index=cf['TROUBLE_SHOOTING']['ES_INDEX_TASK'], id=template_id)
                _ = es_ctrl.index(index=cf['TROUBLE_SHOOTING']['ES_INDEX_TASK'], body=result, id=template_id)

                return JsonResponse({'content': result})
            elif operate == cf['TROUBLE_SHOOTING']['SHOOTING']:
                template_id = request.POST.get(cf['TROUBLE_SHOOTING']['TEMPLATE_ID'])
                selected = request.POST.get(cf['TROUBLE_SHOOTING']['SELECT_TASK'])
                username = request.POST.get(cf['TROUBLE_SHOOTING']['USERNAME'])
                res = es_ctrl.get(index=cf['TROUBLE_SHOOTING']['ES_INDEX_TASK'], id=template_id)['_source']
                replace_res = json.dumps(res)

                before_node = mind_search_id(res['nodeData'], json.loads(selected)['id'])
                after_node = before_node.copy()
                after_node['Status'] = 'shooting'
                after_node['Executor'] = username
                after_node['style'] = {'fontWeight': 'bold', 'color': '#d35400'}
                replace_res = replace_res.replace(json.dumps(before_node), json.dumps(after_node))
                result = json.loads(replace_res)

                _ = es_ctrl.delete(index=cf['TROUBLE_SHOOTING']['ES_INDEX_TASK'], id=template_id)
                _ = es_ctrl.index(index=cf['TROUBLE_SHOOTING']['ES_INDEX_TASK'], body=result, id=template_id)
                return JsonResponse({'content': result})
            elif operate == cf['TROUBLE_SHOOTING']['RELEASE_TASK']:
                template_id = request.POST.get(cf['TROUBLE_SHOOTING']['TEMPLATE_ID'])
                description = request.POST.get(cf['TROUBLE_SHOOTING']['GET_DESCRIPTION'])
                logs = request.FILES.get(cf['TROUBLE_SHOOTING']['GET_LOGS'])
                size = request.POST.get(cf['TROUBLE_SHOOTING']['GET_SIZE'])

                res = es_ctrl.get(index=cf['TROUBLE_SHOOTING']['ES_INDEX_TEMPLATE'], id=template_id)['_source']
                res = json.loads(re.sub(r'\"topic\"', '"Status": "active", "Executor": "pending", "style": {"fontWeight": "bold", "color": "#f1c40e"}, "topic"', json.dumps(res)))
                res['Description'] = description
                res['Status'] = cf['TROUBLE_SHOOTING']['STATUS_ACTIVE']
                res['Date'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                res = es_ctrl.index(index=cf['TROUBLE_SHOOTING']['ES_INDEX_TASK'], body=res)

                if int(size) > 0:
                    base64_images = []
                    for i in range(0, int(size)):
                        image = request.FILES.get(cf['TROUBLE_SHOOTING']['GET_IMAGES']+'_'+str(i))
                        base64_images.append({'name': str(i) + '.jpg', 'content': image_to_base64(image)})
                    data = {'task_id': res['_id'], 'content': base64_images}
                    _ = es_ctrl.index(index=cf['TROUBLE_SHOOTING']['ES_INDEX_TASK_IMAGES'], body=data)

                if logs is not None:
                    cp = file_compress(logs.read())
                    data = {'task_id': res['_id'], 'name': logs.name, 'content': str(cp)}
                    _ = es_ctrl.index(index=cf['TROUBLE_SHOOTING']['ES_INDEX_TASK_LOGS'], body=data)
                return JsonResponse({'content': 'Success'})
            elif operate == cf['TROUBLE_SHOOTING']['UPLOAD_CHECKLIST_IMAGES']:
                username = request.POST.get(cf['ADMIN']['USERNAME'])
                template_id = request.POST.get(cf['TROUBLE_SHOOTING']['TEMPLATE_ID'])
                node_id = request.POST.get(cf['TROUBLE_SHOOTING']['NODE_ID'])
                size = request.POST.get(cf['TROUBLE_SHOOTING']['GET_SIZE'])

                res = es_ctrl.search(index=cf['TROUBLE_SHOOTING']['ES_INDEX_CHECKLIST_IMAGES'], body=query_with([['task_id', template_id], ['node_id', node_id]]))['hits']['hits']
                if len(res) > 0:
                    _id = res[0]['_id']
                    res = res[0]['_source']
                    if int(size) > 0:
                        for i in range(0, int(size)):
                            image = request.FILES.get(cf['TROUBLE_SHOOTING']['GET_IMAGES']+'_'+str(i))
                            res['content'].append({'uuid': uuid.uuid1().hex, 'username': username, 'name': image.name, 'created_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), 'content': image_to_base64(image)})
                        _ = es_ctrl.update(index=cf['TROUBLE_SHOOTING']['ES_INDEX_CHECKLIST_IMAGES'], id=_id, body={'doc': res})
                else:
                    if int(size) > 0:
                        base64_images = []
                        for i in range(0, int(size)):
                            image = request.FILES.get(cf['TROUBLE_SHOOTING']['GET_IMAGES']+'_'+str(i))
                            base64_images.append({'uuid': uuid.uuid1().hex, 'username': username, 'name': image.name, 'created_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), 'content': image_to_base64(image)})
                        data = {'task_id': template_id, 'node_id': node_id, 'content': base64_images}
                        _ = es_ctrl.index(index=cf['TROUBLE_SHOOTING']['ES_INDEX_CHECKLIST_IMAGES'], body=data)
                return JsonResponse({'content': 'Success'})
            elif operate == cf['TROUBLE_SHOOTING']['UPLOAD_CHECKLIST_LOGS']:
                username = request.POST.get(cf['ADMIN']['USERNAME'])
                template_id = request.POST.get(cf['TROUBLE_SHOOTING']['TEMPLATE_ID'])
                node_id = request.POST.get(cf['TROUBLE_SHOOTING']['NODE_ID'])
                size = request.POST.get(cf['TROUBLE_SHOOTING']['GET_SIZE'])

                res = es_ctrl.search(index=cf['TROUBLE_SHOOTING']['ES_INDEX_CHECKLIST_LOGS'], body=query_with([['task_id', template_id], ['node_id', node_id]]))['hits']['hits']
                if len(res) > 0:
                    _id = res[0]['_id']
                    res = res[0]['_source']
                    if int(size) > 0:
                        for i in range(0, int(size)):
                            log = request.FILES.get(cf['TROUBLE_SHOOTING']['GET_LOGS']+'_'+str(i))
                            res['content'].append({'uuid': uuid.uuid1().hex, 'username': username, 'name': log.name, 'created_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), 'content': str(file_compress(log.read()))})
                        _ = es_ctrl.update(index=cf['TROUBLE_SHOOTING']['ES_INDEX_CHECKLIST_LOGS'], id=_id, body={'doc': res})
                else:
                    if int(size) > 0:
                        logs = []
                        for i in range(0, int(size)):
                            log = request.FILES.get(cf['TROUBLE_SHOOTING']['GET_LOGS']+'_'+str(i))
                            logs.append({'uuid': uuid.uuid1().hex, 'username': username, 'name': log.name, 'created_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), 'content': str(file_compress(log.read()))})
                        data = {'task_id': template_id, 'node_id': node_id, 'content': logs}
                        _ = es_ctrl.index(index=cf['TROUBLE_SHOOTING']['ES_INDEX_CHECKLIST_LOGS'], body=data)
                return JsonResponse({'content': 'Success'})
            elif operate == cf['TROUBLE_SHOOTING']['UPLOAD_CHECKLIST_COMMENTS']:
                username = request.POST.get(cf['ADMIN']['USERNAME'])
                template_id = request.POST.get(cf['TROUBLE_SHOOTING']['TEMPLATE_ID'])
                node_id = request.POST.get(cf['TROUBLE_SHOOTING']['NODE_ID'])

                res = es_ctrl.search(index=cf['TROUBLE_SHOOTING']['ES_INDEX_CHECKLIST_COMMENTS'], body=query_with([['task_id', template_id], ['node_id', node_id]]))['hits']['hits']
                if len(res) > 0:
                    _id = res[0]['_id']
                    res = res[0]['_source']
                    comment = request.POST.get(cf['TROUBLE_SHOOTING']['GET_COMMENTS'])
                    res['content'].append({'uuid': uuid.uuid1().hex, 'username': username, 'created_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), 'content': comment})
                    _ = es_ctrl.update(index=cf['TROUBLE_SHOOTING']['ES_INDEX_CHECKLIST_COMMENTS'], id=_id, body={'doc': res})
                else:
                    comments = []
                    comment = request.POST.get(cf['TROUBLE_SHOOTING']['GET_COMMENTS'])
                    comments.append({'uuid': uuid.uuid1().hex, 'username': username, 'created_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), 'content': comment})
                    data = {'task_id': template_id, 'node_id': node_id, 'content': comments}
                    _ = es_ctrl.index(index=cf['TROUBLE_SHOOTING']['ES_INDEX_CHECKLIST_COMMENTS'], body=data)
                return JsonResponse({'content': 'Success'})
        return HttpResponse(404)
    except Exception as e:
        traceback.print_exc()


