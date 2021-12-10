from ru.views import *
from ru.utils.mind_handle import *


def apply_cal_real_mem_addr(df):
    df['addr'] = hex(int(df['Offset'], 16) + int(df['mem_start_addr'], 16))
    return df


def get(request):
    try:
        if request.method == 'GET':
            operate = request.GET.get(cf['DB_TOOL']['OPERATE'])

            if operate == cf['DB_TOOL']['GET_TEST_DATA']:
                return JsonResponse({'content': babel_test_data()})
            elif operate == cf['DB_TOOL']['GET_DB_TOOL_TEST_DATA']:
                driver_entry = request.GET.get('driver_entry')
                return JsonResponse({'content': extract_dbs(driver_entry)})
            elif operate == cf['DB_TOOL']['GET_DB_TOOL_TEST_DATA_BY_NAME']:
                driver_name = request.GET.get('driver_name')
                return JsonResponse({'content': get_dbs_by_drvier_name(driver_name)})
            elif operate == cf['DB_TOOL']['GET_RUNTIME_ELF_FUNCS']:
                pid = 9384
                ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('cat /proc/'+str(pid)+'/maps')
                mem_addr = str(ssh_stdout.read(), encoding="utf-8").split('\n')[0].split(' ')[0].split('-')[0]

                ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(
                    'gcc-nm --format=sysc -C /home/kali/Projects/test/test_hello/demo')
                table = str(ssh_stdout.read(), encoding="utf-8").split('\n')
                res = []
                for line in table[6:]:
                    tmp = re.sub(' ', '', line.replace("\n", "").replace("\t", "")).split("|")
                    if len(tmp) > 7:
                        a = []
                        a.extend(['|'.join(tmp[0:2])])
                        a.extend(tmp[2:])
                        res.append(a)
                    elif ('FUNC|' in line) & ('|.text' in line) & (len(re.sub(' +', ' ', tmp[0])) > 1):
                        res.append(tmp)
                funcs_table = pd.DataFrame(res, columns=['Name', 'Offset', 'Class', 'Type', 'Size', 'Line', 'Section'])
                funcs_table['mem_start_addr'] = mem_addr
                funcs_table = funcs_table.apply(apply_cal_real_mem_addr, axis=1)

                res = {'name': 'functions', 'children': []}
                for item in funcs_table[['Name', 'addr']].values:
                    res['children'].append({'name': item[0], 'addr': item[1]})

                return JsonResponse({'content': res})
            elif operate == cf['DB_TOOL']['EXEC_FUNC']:
                pid = 9384
                mem_addr = request.GET.get(cf['DB_TOOL']['MEM_ADDR'])
                params = request.GET.get(cf['DB_TOOL']['PARAMS'])

                _, _, _ = ssh.exec_command('python3 /home/kali/Projects/test/test_hello/test.py --pid=' + str(pid) +' --func_addr=' + mem_addr+' --params=' + params)
                return JsonResponse({'content': 'success'})
        return HttpResponse(404)
    except Exception as e:
        traceback.print_exc()


def save(request):
    try:
        if request.method == 'POST':
            operate = request.POST.get(cf['DB_TOOL']['OPERATE'])
            if operate == cf['DB_TOOL']['UPDATE_IWD']:
                # docx = BaseDocxHandle(request.FILES.get(cf['DB_TOOL']['FILES']).read())
                docx = BaseDocxHandle("D:\\projects\\test\\db_tool_data\\15519-ROZ1042908_1 PA2.docx")
                data = docx.get_docx_structure()

                tables = []
                for elm in data['content']:
                    if (elm['type'] == 'table') & ('RAIL_ID' in str(elm['content'])):
                        tables.append(elm['content'])

                res = []
                for item in tables[0][['RAIL_ID', 'NO', 'RAIL_Description', 'Voltage', 'Current', 'Temp']].values:
                    if item[3] == 'RO':
                        res.append({'name': item[2] + '_U', 'group': 'volt', 'channelNo': item[0]})
                    elif item[3] == 'R/W':
                        res.append({'name': item[2] + '_U', 'group': 'volt', 'channelNo': item[0]})

                    if item[4] == 'RO':
                        res.append({'name': item[2] + '_I', 'group': 'curr', 'channelNo': item[0]})
                    else:
                        pass

                    if item[5] == 'RO':
                        res.append({'name': item[2] + '_T', 'group': 'temp', 'channelNo': item[0]})
                    else:
                        pass

                data = get_dbs_by_drvier_name('dcDcDrivers:0')
                data = json.dumps(data)

                for item in res:
                    if item['name'] == 'DC_TRX_VCC_U':
                        data = data.replace("/810/dcTrxVccU/channelNo U8 0x03\", \"color\": \"#000000\"", "/810/dcTrxVccU/channelNo U8 " + item['channelNo']+"\", \"color\": \"#DC143C\"")
                    elif item['name'] == 'DC_TRX_VCC_I':
                        data = data.replace("/810/dcTrxVccI/channelNo U8 0x03\", \"color\": \"#000000\"", "/810/dcTrxVccI/channelNo U8 " + item['channelNo']+"\", \"color\": \"#DC143C\"")
                    elif item['name'] == 'DC_TRX_VCC_T':
                        data = data.replace("/810/dcTrxVccTemp/channelNo U8 0x03\", \"color\": \"#000000\"", "/810/dcTrxVccTemp/channelNo U8 " + item['channelNo']+"\", \"color\": \"#DC143C\"")

                return JsonResponse({'content': json.loads(data)})
        return HttpResponse(404)
    except Exception as e:
        traceback.print_exc()
