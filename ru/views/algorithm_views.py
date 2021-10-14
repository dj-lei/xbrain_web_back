from ru.views import *


def cal_cos_sim(vectors_array, embeddings, topk):
    cos_scores = util.pytorch_cos_sim(embeddings, vectors_array)[0]
    top_results = torch.topk(cos_scores, k=topk)
    return top_results


def return_items(vectors, text):
    top_results = cal_cos_sim(list(vectors.vectors.values), text_embedding_ins.encode(text), 20)
    return json.loads(vectors.loc[top_results[1].tolist(), ['id', 'name', 'keywords', 'value']].reset_index(drop=True).to_json(orient='records'))


def get(request):
    try:
        if request.method == 'GET':
            operate = request.GET.get(cf['BABEL']['OPERATE'])
            if operate == 'match_keywords_to_info_source':
                keywords = request.GET.get('keywords')

                result = {'content': []}
                for vectors_keywords in info_source_vectors_keywords:
                    result['content'].append({'id': vectors_keywords['id'], 'top_results': return_items(vectors_keywords['data'], keywords)})
                return JsonResponse(result)
        return HttpResponse(404)
    except Exception as e:
        traceback.print_exc()



