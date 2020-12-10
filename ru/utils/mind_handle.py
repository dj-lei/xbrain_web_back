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


def mind_update_checklist_shooting(node_data, node_id, username):
    if type(node_data) == list:
        for index, elm in enumerate(node_data):
            if elm.__contains__('children'):
                result = mind_update_checklist_shooting(elm['children'], node_id, username)
                if result:
                    elm['Status'] = 'shooting'
                    elm['Executor'] = username
                    elm['style'] = {'fontWeight': 'bold', 'color': '#d35400'}
                    node_data[index]['children'] = result
                    return node_data
            else:
                if elm['id'] == node_id:
                    elm['Status'] = 'shooting'
                    elm['Executor'] = username
                    elm['style'] = {'fontWeight': 'bold', 'color': '#d35400'}
                    node_data[index] = elm
                    return node_data
        return False
    else:
        if node_data.__contains__('children'):
            result = mind_update_checklist_shooting(node_data['children'], node_id, username)
            if result:
                node_data['Status'] = 'shooting'
                node_data['Executor'] = username
                node_data['style'] = {'fontWeight': 'bold', 'color': '#d35400'}
                node_data['children'] = result
                return node_data
        else:
            if node_data['id'] == node_id:
                node_data['Status'] = 'shooting'
                node_data['Executor'] = username
                node_data['style'] = {'fontWeight': 'bold', 'color': '#d35400'}
                return node_data
    return node_data