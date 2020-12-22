import json


def mind_get_list(node_data):
    temp = []
    if type(node_data) == list:
        for elm in node_data:
            if elm.__contains__('children'):
                temp.extend(mind_get_list(elm['children']))
            else:
                temp.append([elm['id'], elm['topic'], elm['Status'], elm['Executor']])
    else:
        if node_data.__contains__('children'):
            temp.extend(mind_get_list(node_data['children']))
        else:
            temp.append([node_data['id'], node_data['topic'], node_data['Status'], node_data['Executor']])
    return temp


def mind_search_id(node_data, node_id):
    if type(node_data) == list:
        for elm in node_data:
            if elm['id'] == node_id:
                return elm
            else:
                if elm.__contains__('children'):
                    temp = mind_search_id(elm['children'], node_id)
                    if temp:
                        return temp
                    else:
                        continue
                else:
                    continue
    else:
        if node_data['id'] == node_id:
            return node_data
        elif node_data.__contains__('children'):
            return mind_search_id(node_data['children'], node_id)
        else:
            return []
    return []


def mind_color_update(node_data):
    flag_list = []
    if type(node_data) == list:
        for i, elm in enumerate(node_data):
            if elm.__contains__('children'):
                flag, sub_node_data = mind_color_update(elm['children'])
                elm['children'] = sub_node_data
                if flag:
                    elm['style'] = {'fontWeight': 'bold', 'color': '#2ecc71'}
                    elm['Status'] = 'close'
                node_data[i] = elm
                flag_list.append(flag)
            else:
                if elm['Status'] == 'close':
                    continue
                else:
                    flag_list.append(False)
        if False in flag_list:
            return False, node_data
        return True, node_data
    else:
        if node_data.__contains__('children'):
            flag, sub_node_data = mind_color_update(node_data['children'])
            node_data['children'] = sub_node_data
            if flag:
                node_data['style'] = {'fontWeight': 'bold', 'color': '#2ecc71'}
                node_data['Status'] = 'close'
        else:
            if node_data['Status'] == 'close':
                node_data['style'] = {'fontWeight': 'bold', 'color': '#2ecc71'}
    return node_data


def mind_export_to_csv(node_data, node=None):
    temp = []
    node = node if node else ''
    if type(node_data) == list:
        for elm in node_data:
            if elm.__contains__('children'):
                temp.extend(mind_export_to_csv(elm['children'], node+'/'+elm['topic']))
            else:
                temp.append([elm['topic'], node, elm['Status'], elm['Executor']])
    else:
        if node_data.__contains__('children'):
            temp.extend(mind_export_to_csv(node_data['children'], node+'/'+node_data['topic']))
        else:
            temp.append([node_data['topic'], node, node_data['Status'], node_data['Executor']])
    return temp


def mind_update_checklist_asterisk(node_data, node_id):
    if type(node_data) == list:
        for index, elm in enumerate(node_data):
            if elm.__contains__('children'):
                result = mind_update_checklist_asterisk(elm['children'], node_id)
                if result:
                    node_data[index]['children'] = result
                    return node_data
            else:
                if elm['id'] == node_id:
                    node_data[index]['topic'] = elm['topic'].replace(' (*)','') if ' (*)' in elm['topic'] else elm['topic'] + ' (*)'
                    return node_data
        return False
    else:
        if node_data.__contains__('children'):
            result = mind_update_checklist_asterisk(node_data['children'], node_id)
            if result:
                node_data['children'] = result
                return node_data
        else:
            if node_data['id'] == node_id:
                node_data['topic'] = node_data['topic'].replace(' (*)','') if ' (*)' in node_data['topic'] else node_data['topic'] + ' (*)'
                return node_data
    return node_data


def mind_update_checklist_shooting(node_data, node_id, username, operate='close'):
    if type(node_data) == list:
        for index, elm in enumerate(node_data):
            if elm.__contains__('children'):
                result = mind_update_checklist_shooting(elm['children'], node_id, username, operate)
                if result:
                    if operate == 'shooting':
                        elm['Status'] = 'shooting'
                        elm['Executor'] = username
                        elm['style'] = {'fontWeight': 'bold', 'color': '#d35400'}
                        node_data[index]['children'] = result
                        return node_data
                    if (operate == 'close') & ('shooting' not in json.dumps(result)):
                        elm['Status'] = 'close'
                        elm['Executor'] = username
                        elm['style'] = {'fontWeight': 'bold', 'color': '#2ecc71'}
                        node_data[index]['children'] = result
                        return node_data
            else:
                if elm['id'] == node_id:
                    elm['Status'] = operate if operate == 'shooting' else 'close'
                    elm['Executor'] = username
                    elm['style'] = {'fontWeight': 'bold', 'color': '#d35400'} if operate == 'shooting' else {'fontWeight': 'bold', 'color': '#2ecc71'}
                    node_data[index] = elm
                    return node_data
        return False
    else:
        if node_data.__contains__('children'):
            result = mind_update_checklist_shooting(node_data['children'], node_id, username, operate)
            if result:
                node_data['Status'] = operate if operate == 'shooting' else 'close'
                node_data['Executor'] = username
                node_data['style'] = {'fontWeight': 'bold', 'color': '#d35400'} if operate == 'shooting' else {'fontWeight': 'bold', 'color': '#2ecc71'}
                node_data['children'] = result
                return node_data
        else:
            if node_data['id'] == node_id:
                node_data['Status'] = operate if operate == 'shooting' else 'close'
                node_data['Executor'] = username
                node_data['style'] = {'fontWeight': 'bold', 'color': '#d35400'} if operate == 'shooting' else {'fontWeight': 'bold', 'color': '#2ecc71'}
                return node_data
    return node_data


def mind_update_template_to_task(updated_template, task):
    if type(updated_template) == list:
        for index, elm in enumerate(updated_template):
            if elm.__contains__('children'):
                updated_template[index]['children'] = mind_update_template_to_task(elm['children'], task)
                temp_dict = mind_search_id(task, updated_template[index]['id'])
                if len(temp_dict) > 0:
                    updated_template[index]['Status'] = temp_dict['Status']
                    updated_template[index]['Executor'] = temp_dict['Executor']
                    updated_template[index]['style'] = temp_dict['style']
                else:
                    updated_template[index]['Status'] = 'active'
                    updated_template[index]['Executor'] = 'pending'
                    updated_template[index]['style'] = {"fontWeight": "bold", "color": "#f39c11"}
            else:
                temp_dict = mind_search_id(task, elm['id'])
                if len(temp_dict) > 0:
                    elm['Status'] = temp_dict['Status']
                    elm['Executor'] = temp_dict['Executor']
                    elm['style'] = temp_dict['style']
                else:
                    elm['Status'] = 'active'
                    elm['Executor'] = 'pending'
                    elm['style'] = {"fontWeight": "bold", "color": "#f39c11"}
                updated_template[index] = elm
        return updated_template
    else:
        if updated_template.__contains__('children'):
            updated_template['children'] = mind_update_template_to_task(updated_template['children'], task)
        else:
            temp_dict = mind_search_id(task, updated_template['id'])
            if len(temp_dict) > 0:
                updated_template['Status'] = temp_dict['Status']
                updated_template['Executor'] = temp_dict['Executor']
                updated_template['style'] = temp_dict['style']
            else:
                updated_template['Status'] = 'active'
                updated_template['Executor'] = 'pending'
                updated_template['style'] = {"fontWeight": "bold", "color": "#f39c11"}
    return updated_template