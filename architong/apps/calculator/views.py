import json
import os

from django.http import HttpResponse
from django.shortcuts import render


# 열관류율 계산기
def uvalue(request):
    # GET 요청이면 지역,용도 선택 페이지를 렌더링한다
    if request.method == 'GET':
        return render(request, 'calculator/uvalue_init.html')

    # POST 요청이면 열관류율 계산기 페이지를 렌더링한다
    elif request.method == 'POST':
        context = {
            "sido1": request.POST.get('sido1', ''),
            "gugun1": request.POST.get('gugun1', ''),
            "locale": request.POST.get('locale', ''),
            "use": request.POST.get('use', '')
        }
        return render(request, 'calculator/uvalue.html', context)


# 열관류율 계산기 모바일
def uvalue_m(request):
    return render(request, 'calculator/uvalue_mobile.html')


# 열관류율 계산기 초기 데이터 로딩
def uvalue_data(request):
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uValueCalc.json')
    with open(json_path, 'r', encoding='UTF8') as f:
        json_file = json.load(f)
    return HttpResponse(json.dumps(json_file), content_type="application/json")
