import json
import os

from django.http import HttpResponse
from django.shortcuts import render

# 웹 메인 페이지 렌더링
def uvalue(request):
    return render(request, 'calculator/uvalue.html')

# 모바일 메인 페이지 렌더링
def uvalue_m(request):
    return render(request, 'calculator/uvalue_mobile.html')


# 열관류율 계산기 초기 데이터 로딩
def uvalue_data(request):
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uValueCalc.json')
    with open(json_path, 'r', encoding='UTF8') as f:
        json_file = json.load(f)
    return HttpResponse(json.dumps(json_file), content_type="application/json")
