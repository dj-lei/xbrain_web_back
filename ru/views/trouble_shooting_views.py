from ru.views import *
from ru.utils.mind_handle import *


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
            elif operate == cf['TROUBLE_SHOOTING']['RELEASE_TASK']:
                template_id = request.GET.get(cf['TROUBLE_SHOOTING']['TEMPLATE_ID'])
                res = es_ctrl.get(index=cf['TROUBLE_SHOOTING']['ES_INDEX_TEMPLATE'], id=template_id)['_source']
                res = json.loads(re.sub(r'\"topic\"', '"Status": "active", "Executor": "pending", "style": {"fontWeight": "bold", "color": "#f1c40e"}, "topic"', json.dumps(res)))
                res['Status'] = cf['TROUBLE_SHOOTING']['STATUS_ACTIVE']
                res['Date'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                _ = es_ctrl.index(index=cf['TROUBLE_SHOOTING']['ES_INDEX_TASK'], body=res)
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
        return HttpResponse(404)
    except Exception as e:
        traceback.print_exc()


def save(request):
    try:
        if request.method == 'POST':
            operate = request.POST.get(cf['TROUBLE_SHOOTING']['OPERATE'])
            if operate == cf['TROUBLE_SHOOTING']['NEW_ADD']:
                data = request.POST.get(cf['TROUBLE_SHOOTING']['GET_DATA'])
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
        return HttpResponse(404)
    except Exception as e:
        traceback.print_exc()


