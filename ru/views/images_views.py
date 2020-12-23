from ru.views import *


def upload(request):
    try:
        if request.method == 'POST':
            image = request.FILES.get(cf['IMAGES']['GET_IMAGE'])
            content = image_to_base64(image)
            res = es_ctrl.index(index=cf['IMAGES']['ES_INDEX'], body={'content': content})
            if profile == 'product':
                addr = server_address
            else:
                addr = server_address + ':8000'
            return JsonResponse({'success': 1, 'file': {'url': 'http://'+addr+'/ru/images/get?image_id='+res['_id']}})
        return HttpResponse(404)
    except Exception as e:
        traceback.print_exc()


def get(request):
    try:
        if request.method == 'GET':
            image_id = request.GET.get(cf['IMAGES']['IMAGE_ID'])
            _id = es_ctrl.get(index=cf['IMAGES']['ES_INDEX'], id=image_id)
            image_data = base64_to_image(_id['_source']['content'])
            return HttpResponse(image_data, content_type="image/png")
        return HttpResponse(404)
    except Exception as e:
        traceback.print_exc()