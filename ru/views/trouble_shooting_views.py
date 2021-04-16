from ru.views import *
from ru.utils.mind_handle import *
from io import BytesIO
from PIL import Image


def get(request):
    try:
        if request.method == 'GET':
            operate = request.GET.get(cf['TROUBLE_SHOOTING']['OPERATE'])
            if operate == cf['TROUBLE_SHOOTING']['GET_TEMPLATE_TITLES']:
                res = es_ctrl.search(index=cf['TROUBLE_SHOOTING']['ES_INDEX_TEMPLATE'], size=200)
                data = res['hits']['hits']
                result = []
                if len(data) > 0:
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
                res = es_ctrl.search(index=cf['TROUBLE_SHOOTING']['ES_INDEX_TASK'], size=200)
                data = res['hits']['hits']
                result = []
                if len(data) > 0:
                    for elm in data:
                        result.append({'id': elm['_id'], 'TaskName': elm['_source']['TemplateName'], 'Status': elm['_source']['Status'],
                                       'Group': elm['_source']['Group'] if "Group" in elm['_source'].keys() else 'unknown', 'Date': elm['_source']['Date']})
                return JsonResponse({'content': result})
            elif operate == cf['TROUBLE_SHOOTING']['GET_TASK']:
                template_id = request.GET.get(cf['TROUBLE_SHOOTING']['TEMPLATE_ID'])
                res = es_ctrl.get(index=cf['TROUBLE_SHOOTING']['ES_INDEX_TASK'], id=template_id)
                return JsonResponse({'content': res['_source'], 'id': template_id})
            elif operate == cf['TROUBLE_SHOOTING']['DELETE_TASK']:
                template_id = request.GET.get(cf['TROUBLE_SHOOTING']['TEMPLATE_ID'])

                # _id = es_ctrl.search(index=cf['TROUBLE_SHOOTING']['ES_INDEX_CHECKLIST_IMAGES'],
                #                      body=query_with([['task_id', template_id]]))['hits']['hits']
                # if len(_id) > 0:
                #     for i in range(0, len(_id)):
                #         _ = es_ctrl.delete(index=cf['TROUBLE_SHOOTING']['ES_INDEX_CHECKLIST_IMAGES'], id=_id[i]['_id'])

                _id = es_ctrl.search(index=cf['TROUBLE_SHOOTING']['ES_INDEX_CHECKLIST_LOGS'],
                                     body=query_with([['task_id', template_id]]), size=200)['hits']['hits']
                if len(_id) > 0:
                    for i in range(0, len(_id)):
                        _ = es_ctrl.delete(index=cf['TROUBLE_SHOOTING']['ES_INDEX_CHECKLIST_LOGS'], id=_id[i]['_id'])

                _id = es_ctrl.search(index=cf['TROUBLE_SHOOTING']['ES_INDEX_CHECKLIST_COMMENTS'],
                                     body=query_with([['task_id', template_id]]), size=200)['hits']['hits']
                if len(_id) > 0:
                    for i in range(0, len(_id)):
                        _ = es_ctrl.delete(index=cf['TROUBLE_SHOOTING']['ES_INDEX_CHECKLIST_COMMENTS'], id=_id[i]['_id'])

                _ = es_ctrl.delete(index=cf['TROUBLE_SHOOTING']['ES_INDEX_TASK'], id=template_id)

                return JsonResponse({'content': 'Success'})
            elif operate == cf['TROUBLE_SHOOTING']['CLOSE_TASK']:
                template_id = request.GET.get(cf['TROUBLE_SHOOTING']['TEMPLATE_ID'])
                res = es_ctrl.get(index=cf['TROUBLE_SHOOTING']['ES_INDEX_TASK'], id=template_id)['_source']
                res['Status'] = 'close'
                res['Date'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                replace_res = json.dumps(res).replace('#f1c40e', '#2ecc71').replace('active', 'close')
                res = json.loads(replace_res)

                _ = es_ctrl.update(index=cf['TROUBLE_SHOOTING']['ES_INDEX_TASK'], body={'doc': res}, id=template_id)

                return JsonResponse({'content': 'Success'})
            elif operate == cf['TROUBLE_SHOOTING']['GET_TASK_DETAILS']:
                template_id = request.GET.get(cf['TROUBLE_SHOOTING']['TEMPLATE_ID'])
                node_id = request.GET.get(cf['TROUBLE_SHOOTING']['NODE_ID'])
                res = es_ctrl.get(index=cf['TROUBLE_SHOOTING']['ES_INDEX_TASK'], id=template_id)
                data = mind_get_list(mind_search_id(res['_source']['nodeData'], node_id))

                result = []
                for elm in data:
                    result.append({'id': elm[0], 'Task': elm[1], 'Status': elm[2], 'Schedule': elm[3]})
                return JsonResponse({'content': result, 'id': template_id})
            elif operate == cf['TROUBLE_SHOOTING']['GET_CHECKLIST_IMAGES']:
                template_id = request.GET.get(cf['TROUBLE_SHOOTING']['TEMPLATE_ID'])
                node_id = request.GET.get(cf['TROUBLE_SHOOTING']['NODE_ID'])
                res = es_ctrl.search(index=cf['TROUBLE_SHOOTING']['ES_INDEX_CHECKLIST_IMAGES'], body=query_with([['task_id', template_id], ['node_id', node_id]]), size=200)['hits']['hits']
                result = res[0]['_source']['content'] if len(res) > 0 else []
                return JsonResponse({'content': result})
            elif operate == cf['TROUBLE_SHOOTING']['DELETE_CHECKLIST_IMAGE']:
                template_id = request.GET.get(cf['TROUBLE_SHOOTING']['TEMPLATE_ID'])
                node_id = request.GET.get(cf['TROUBLE_SHOOTING']['NODE_ID'])
                uuid_id = request.GET.get(cf['TROUBLE_SHOOTING']['UUID_ID'])
                res = es_ctrl.search(index=cf['TROUBLE_SHOOTING']['ES_INDEX_CHECKLIST_IMAGES'], body=query_with([['task_id', template_id], ['node_id', node_id]]), size=200)['hits']['hits'][0]

                for index, elm in enumerate(res['_source']['content']):
                    if elm['uuid'] == uuid_id:
                        res['_source']['content'].pop(index)
                        _ = es_ctrl.update(index=cf['TROUBLE_SHOOTING']['ES_INDEX_CHECKLIST_IMAGES'], id=res['_id'], body={'doc': res['_source']})
                        return JsonResponse({'content': 'Success'})
                return HttpResponse(404)
            elif operate == cf['TROUBLE_SHOOTING']['GET_CHECKLIST_LOGS']:
                template_id = request.GET.get(cf['TROUBLE_SHOOTING']['TEMPLATE_ID'])
                node_id = request.GET.get(cf['TROUBLE_SHOOTING']['NODE_ID'])
                res = es_ctrl.search(index=cf['TROUBLE_SHOOTING']['ES_INDEX_CHECKLIST_LOGS'], body=query_with([['task_id', template_id], ['node_id', node_id]]), size=200)['hits']['hits']
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
                res = es_ctrl.search(index=cf['TROUBLE_SHOOTING']['ES_INDEX_CHECKLIST_LOGS'], body=query_with([['task_id', template_id], ['node_id', node_id]]), size=200)['hits']['hits'][0]['_source']['content']

                for elm in res:
                    if elm['uuid'] == uuid_id:
                        response = HttpResponse(file_decompress(elm['content']), 'application/txt')
                        response['Content-Disposition'] = elm['name']
                        response['Access-Control-Expose-Headers'] = 'Content-Disposition'
                        return response
                return HttpResponse(404)
            elif operate == cf['TROUBLE_SHOOTING']['DELETE_CHECKLIST_LOG']:
                template_id = request.GET.get(cf['TROUBLE_SHOOTING']['TEMPLATE_ID'])
                node_id = request.GET.get(cf['TROUBLE_SHOOTING']['NODE_ID'])
                uuid_id = request.GET.get(cf['TROUBLE_SHOOTING']['UUID_ID'])
                res = es_ctrl.search(index=cf['TROUBLE_SHOOTING']['ES_INDEX_CHECKLIST_LOGS'], body=query_with([['task_id', template_id], ['node_id', node_id]]), size=200)['hits']['hits'][0]

                for index, elm in enumerate(res['_source']['content']):
                    if elm['uuid'] == uuid_id:
                        res['_source']['content'].pop(index)
                        _ = es_ctrl.update(index=cf['TROUBLE_SHOOTING']['ES_INDEX_CHECKLIST_LOGS'], id=res['_id'], body={'doc': res['_source']})
                        return JsonResponse({'content': 'Success'})
                return HttpResponse(404)
            elif operate == cf['TROUBLE_SHOOTING']['GET_CHECKLIST_COMMENTS']:
                template_id = request.GET.get(cf['TROUBLE_SHOOTING']['TEMPLATE_ID'])
                node_id = request.GET.get(cf['TROUBLE_SHOOTING']['NODE_ID'])
                res = es_ctrl.search(index=cf['TROUBLE_SHOOTING']['ES_INDEX_CHECKLIST_COMMENTS'], body=query_with([['task_id', template_id], ['node_id', node_id]]), size=200)['hits']['hits']
                result = []
                if len(res) > 0:
                    res = res[0]['_source']['content']
                    for elm in res:
                        result.append({'uuid': elm['uuid'], 'username': elm['username'], 'created_time': elm['created_time'], 'comment': elm['content']})
                return JsonResponse({'content': result})
            elif operate == cf['TROUBLE_SHOOTING']['EXPORT_TASK']:
                template_id = request.GET.get(cf['TROUBLE_SHOOTING']['TEMPLATE_ID'])
                res = es_ctrl.get(index=cf['TROUBLE_SHOOTING']['ES_INDEX_TASK'], id=template_id)
                data = res['_source']['nodeData']['children']
                temp = mind_export_to_csv(data)
                temp = pd.DataFrame(temp, columns=['Tasks', 'Responsible', 'Status', 'Schedule'])
                temp['Status'] = temp['Status'].map({0: 'GoOn', 1: 'Done', 2: 'Uncertain', 3: 'Shooting'})

                excel_file = BytesIO()
                xlwriter = pd.ExcelWriter(excel_file, engine='xlsxwriter')
                temp.to_excel(xlwriter, 'sheet1')
                xlwriter.save()

                excel_file.seek(0)
                response = HttpResponse(excel_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                response['Content-Disposition'] = res['_source']['TemplateName']
                response['Access-Control-Expose-Headers'] = 'Content-Disposition'
                return response
            elif operate == cf['TROUBLE_SHOOTING']['UPDATE_CHECKLIST_ASTERISK']:
                template_id = request.GET.get(cf['TROUBLE_SHOOTING']['TEMPLATE_ID'])
                node_id = request.GET.get(cf['TROUBLE_SHOOTING']['NODE_ID'])

                res = es_ctrl.get(index=cf['TROUBLE_SHOOTING']['ES_INDEX_TASK'], id=template_id)
                res['_source']['nodeData'] = mind_update_checklist_asterisk(res['_source']['nodeData'], node_id)
                _ = es_ctrl.update(index=cf['TROUBLE_SHOOTING']['ES_INDEX_TASK'], id=template_id, body={'doc': res['_source']})
                return JsonResponse({'content': res['_source'], 'id': template_id})
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

                data = json.loads(re.sub(", \"children\": \[\]", '', json.dumps(data)))
                _ = es_ctrl.index(index=cf['TROUBLE_SHOOTING']['ES_INDEX_TEMPLATE'], body=data, id=template_id)

                res = es_ctrl.search(index=cf['TROUBLE_SHOOTING']['ES_INDEX_TASK'],
                                     body=query_with([['template_id', template_id]]), size=200)['hits']['hits']

                if len(res) > 0:
                    for elm in res:
                        elm['_source']['nodeData'] = mind_update_template_to_task(json.loads(data)['nodeData'], elm['_source']['nodeData'])
                        elm = json.loads(re.sub(", \"children\": \[\]", '', json.dumps(elm)))
                        _ = es_ctrl.update(index=cf['TROUBLE_SHOOTING']['ES_INDEX_TASK'], body={'doc': elm['_source']}, id=elm['_id'])

                return JsonResponse({'content': 'Success'})
            elif operate == cf['TROUBLE_SHOOTING']['UPDATE_TASK']:
                template_id = request.POST.get(cf['TROUBLE_SHOOTING']['TEMPLATE_ID'])
                selected = request.POST.get(cf['TROUBLE_SHOOTING']['SELECT_TASK'])
                username = request.POST.get(cf['TROUBLE_SHOOTING']['USERNAME'])
                res = es_ctrl.get(index=cf['TROUBLE_SHOOTING']['ES_INDEX_TASK'], id=template_id)['_source']

                for select in json.loads(selected):
                    res['nodeData'] = mind_update_checklist_shooting(res['nodeData'], select['id'], username, 'close')
                _ = es_ctrl.update(index=cf['TROUBLE_SHOOTING']['ES_INDEX_TASK'], body={'doc': res}, id=template_id)
                return JsonResponse({'content': res})
            elif operate == cf['TROUBLE_SHOOTING']['APPLY']:
                template_id = request.POST.get(cf['TROUBLE_SHOOTING']['TEMPLATE_ID'])
                selected = request.POST.get(cf['TROUBLE_SHOOTING']['SELECT_TASK'])
                username = request.POST.get(cf['TROUBLE_SHOOTING']['USERNAME'])
                res = es_ctrl.get(index=cf['TROUBLE_SHOOTING']['ES_INDEX_TASK'], id=template_id)['_source']

                for select in json.loads(selected):
                    temp = mind_search_id(res['nodeData'], select['id'])
                    temp['Schedule'] = select['Schedule']
                    temp['Status'] = select['Status']
                    if select['Status'] == 0:
                        temp['style'] = {"fontWeight": "bold", "color": "#f39c11"}
                    elif select['Status'] == 1:
                        temp['style'] = {"fontWeight": "bold", "color": "#00FF00"}
                    elif select['Status'] == 2:
                        temp['style'] = {"fontWeight": "bold", "color": "#C0C0C0"}
                    elif select['Status'] == 3:
                        temp['style'] = {"fontWeight": "bold", "color": "#FF0000"}
                    res = json.loads(re.sub(json.dumps(mind_search_id(res['nodeData'], select['id'])), json.dumps(temp), json.dumps(res)))
                _ = es_ctrl.update(index=cf['TROUBLE_SHOOTING']['ES_INDEX_TASK'], body={'doc': res}, id=template_id)
                return JsonResponse({'content': res})
            elif operate == cf['TROUBLE_SHOOTING']['RELEASE_TASK']:
                template_id = request.POST.get(cf['TROUBLE_SHOOTING']['TEMPLATE_ID'])
                username = request.POST.get(cf['ADMIN']['USERNAME'])
                group = request.POST.get(cf['TROUBLE_SHOOTING']['GROUP'])
                description = request.POST.get(cf['TROUBLE_SHOOTING']['GET_DESCRIPTION'])
                logs_size = request.POST.get(cf['TROUBLE_SHOOTING']['GET_LOGS_SIZE'])

                res = es_ctrl.get(index=cf['TROUBLE_SHOOTING']['ES_INDEX_TEMPLATE'], id=template_id)['_source']
                res = json.loads(re.sub(r'\"topic\"', '"Status": 0, "Schedule":0, "Executor": "pending", "style": {"fontWeight": "bold", "color": "#f39c11"}, "topic"', json.dumps(res)).replace(', \"children\": []', ''))
                res['template_id'] = template_id
                res['Description'] = json.loads(description)
                res['Group'] = group
                res['Status'] = cf['TROUBLE_SHOOTING']['STATUS_ACTIVE']
                res['Date'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                res = es_ctrl.index(index=cf['TROUBLE_SHOOTING']['ES_INDEX_TASK'], body=res)

                if int(logs_size) > 0:
                    logs = []
                    for i in range(0, int(logs_size)):
                        log = request.FILES.get(cf['TROUBLE_SHOOTING']['GET_LOGS']+'_'+str(i))
                        logs.append({'uuid': uuid.uuid1().hex, 'username': username, 'name': log.name, 'created_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), 'content': str(file_compress(log.read()))})
                    data = {'task_id': res['_id'], 'node_id': 'root', 'content': logs}
                    _ = es_ctrl.index(index=cf['TROUBLE_SHOOTING']['ES_INDEX_CHECKLIST_LOGS'], body=data)
                return JsonResponse({'content': 'Success'})
            elif operate == cf['TROUBLE_SHOOTING']['UPLOAD_CHECKLIST_IMAGES']:
                username = request.POST.get(cf['ADMIN']['USERNAME'])
                template_id = request.POST.get(cf['TROUBLE_SHOOTING']['TEMPLATE_ID'])
                node_id = request.POST.get(cf['TROUBLE_SHOOTING']['NODE_ID'])
                size = request.POST.get(cf['TROUBLE_SHOOTING']['GET_IMAGES_SIZE'])

                res = es_ctrl.search(index=cf['TROUBLE_SHOOTING']['ES_INDEX_CHECKLIST_IMAGES'], body=query_with([['task_id', template_id], ['node_id', node_id]]), size=200)['hits']['hits']
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
                size = request.POST.get(cf['TROUBLE_SHOOTING']['GET_LOGS_SIZE'])

                res = es_ctrl.search(index=cf['TROUBLE_SHOOTING']['ES_INDEX_CHECKLIST_LOGS'], body=query_with([['task_id', template_id], ['node_id', node_id]]), size=200)['hits']['hits']
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

                res = es_ctrl.search(index=cf['TROUBLE_SHOOTING']['ES_INDEX_CHECKLIST_COMMENTS'], body=query_with([['task_id', template_id], ['node_id', node_id]]), size=200)['hits']['hits']
                if len(res) > 0:
                    _id = res[0]['_id']
                    res = res[0]['_source']
                    comment = json.loads(request.POST.get(cf['TROUBLE_SHOOTING']['GET_COMMENTS']))
                    res['content'].append({'uuid': uuid.uuid1().hex, 'username': username, 'created_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), 'content': comment})
                    _ = es_ctrl.update(index=cf['TROUBLE_SHOOTING']['ES_INDEX_CHECKLIST_COMMENTS'], id=_id, body={'doc': res})
                else:
                    comments = []
                    comment = json.loads(request.POST.get(cf['TROUBLE_SHOOTING']['GET_COMMENTS']))
                    comments.append({'uuid': uuid.uuid1().hex, 'username': username, 'created_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), 'content': comment})
                    data = {'task_id': template_id, 'node_id': node_id, 'content': comments}
                    _ = es_ctrl.index(index=cf['TROUBLE_SHOOTING']['ES_INDEX_CHECKLIST_COMMENTS'], body=data)
                return JsonResponse({'content': 'Success'})
        return HttpResponse(404)
    except Exception as e:
        traceback.print_exc()


