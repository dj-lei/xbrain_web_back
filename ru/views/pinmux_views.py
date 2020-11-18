from ru.views import *

from ru.utils.create_pinmux_config_one_click_9_18 import PinmuxConfig


def get(request):
    try:
        if request.method == 'GET':
            operate = request.GET.get(cf['PINMUX']['OPERATE'])
            if operate == cf['PINMUX']['GET_TEMPLATE_TITLES']:
                res = es_ctrl.search(index=cf['PINMUX']['ES_INDEX'])
                data = res['hits']['hits']
                result = []
                for elm in data:
                    result.append({'id': elm['_id'], 'TemplateName': elm['_source']['TemplateName'],
                                   'Asic': elm['_source']['Asic'], 'Date': elm['_source']['Date']})
                return JsonResponse({'content': result})
            elif operate == cf['PINMUX']['DOWNLOAD']:
                template_id = request.GET.get("template_id")
                res = es_ctrl.get(index=cf['PINMUX']['ES_INDEX'], id=template_id)['_source']
                response = HttpResponse(res['File'], 'application/txt')
                response['Content-Disposition'] = 'attachment; filename={0}'.format(res['TemplateName']+'.txt')
                return response
            elif operate == cf['PINMUX']['DELETE_TEMPLATE']:
                template_id = request.GET.get(cf['PINMUX']['TEMPLATE_ID'])
                res = es_ctrl.delete(index=cf['PINMUX']['ES_INDEX'], id=template_id)
                return JsonResponse({'content': 'Success'})
            elif operate == cf['PINMUX']['DIFF']:
                template_id_a = request.GET.get(cf['PINMUX']['TEMPLATE_ID_A'])
                template_id_b = request.GET.get(cf['PINMUX']['TEMPLATE_ID_B'])
                a = es_ctrl.get(index=cf['PINMUX']['ES_INDEX'], id=template_id_a)['_source']['File'].split('\n')
                b = es_ctrl.get(index=cf['PINMUX']['ES_INDEX'], id=template_id_b)['_source']['File'].split('\n')
                content = difflib.HtmlDiff().make_file(a, b, context=True, numlines=5)
                return HttpResponse(content)
        return HttpResponse(404)
    except Exception as e:
        traceback.print_exc()


def save(request):
    try:
        if request.method == 'POST':
            upload_file = request.FILES.get(cf['PINMUX']['GET_DATA'])
            asic = request.POST.get(cf['PINMUX']['ASIC'])
            file_name = request.POST.get(cf['PINMUX']['FILE_NAME'])
            date = request.POST.get(cf['PINMUX']['DATE'])
            origin_file = file_name
            outfile = origin_file + '.txt'

            table = pd.read_excel(upload_file, converters={'Configuration Pull-up/down [PE:PS]': str,
                                                          'Used impedance selection IMPSEL[1:2]': str})
            table1 = table.iloc[0:len(table) - 1]
            table2 = table.iloc[[len(table) - 1]]
            infile = 'temp.csv'
            table1.to_csv(infile, sep=',', encoding='utf-8', header=True, index=False)
            table2.to_csv(infile, sep=',', encoding='utf-8', header=False, index=False, mode='a', line_terminator=" ")

            config = PinmuxConfig(origin_file, infile, outfile, None, asic, '')
            config.create()
            os.remove(infile)

            with open('ru/tmp/temp.txt') as file:
                data = {'TemplateName': file_name, 'Asic': asic, 'Date': date, 'File': file.read()}
                res = es_ctrl.index(index=cf['PINMUX']['ES_INDEX'], doc_type=cf['PINMUX']['ES_TYPE'], body=data)
                return JsonResponse({'content': 'Success'})
        return HttpResponse(404)
    except Exception as e:
        traceback.print_exc()


def index(request):
    return HttpResponse("Hello World!")
#
#
# def test(request):
#     doc_handle = BaseDocxHandle('test.docx')
#     data = doc_handle.get_docx_structure()
#     catalog = doc_handle.get_catalog()
#
#     result = markdown.markdown("# " + data['name'] + " \r")
#     count = 0
#     image_num = 0
#
#     for elm in data['content']:
#         if elm['type'] == 'text':
#             if 'Heading ' in elm['style']:
#                 level = ''.join(["#" for _ in range(0, int(elm['style'].split(' ')[1]) + 1)]) + ' '
#                 result = result + markdown.markdown(level + catalog['catalog'][count]['chapter'] + ' ' + elm['content'] + " \r")
#                 count += 1
#             else:
#                 if 'List' in elm['style']:
#                     result = result + markdown.markdown("* " + elm['content'] + " \r")
#                 else:
#                     result = result + markdown.markdown(elm['content'] + " \r")
#
#         if elm['type'] == 'image':
#             img = Image.open(BytesIO(bytes(elm['content'])))
#             img = img.resize((450, 300), Image.ANTIALIAS)
#             img.save('ru/assets/image' + str(image_num) + '.png')
#             result = result + markdown.markdown("![test](get_image/?path=ru/assets/image" + str(image_num) + ".png)" + " \r").replace(
#                 "src=\"", "src=\"http://localhost:8000/es/"
#             )
#             image_num += 1
#
#         if elm['type'] == 'table':
#             table = elm['content'].to_markdown(index=False)
#             result = result + markdown.markdown(table + " \r", extensions=['markdown.extensions.fenced_code',
#                                               'markdown.extensions.tables']).replace('table',
#                                                                                      'table border="1" cellspacing="0"')
#
#     return render(request, 'test.html', {'content': result})
#
#
# def get_image(request):
#     image_data = open(request.GET.get("path"), "rb").read()
#     # image_data = base64.b64encode(image_data)
#     return HttpResponse(image_data, content_type="image/jpeg")