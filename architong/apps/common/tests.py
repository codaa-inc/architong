from django.test import TestCase

# Create your tests here.
from xml.etree import ElementTree

str_xml = '''<animals>
                <animal>
                    <name>lion</name>
                    <lifespan>13</lifespan>
                </animal>
                <animal>
                    <name>tiger</name>
                    <lifespan>17</lifespan>
                </animal>
            </animals>'''
root_element = ElementTree.fromstring(str_xml) # 문자열에서 XML을 파싱합니다
animals = [] # 동물리스트를 저장할 list 초기화한다
iter_element = root_element.iter(tag="animal") # animal태그 iterator를 가져옵니다
print(iter_element)
for element in iter_element: # animal태그를 순회합니다
    animal = {} # 각 동물을 저장할 dict 초기화한다
    animal['name'] = element.find("name").text # name태그 값을 저장합니다
    animal['lifespan'] = element.find("lifespan").text # lefespan태그 값을 저장합니다
    animals.append(animal) # 동물리스트에 동물정보를 저장합니다
print(animals) # 결과를 출력한다