import requests
import xml.etree.ElementTree as ET

url = "http://api.kcisa.kr/openapi/service/rest/meta12/getKSCD0802?serviceKey=967feea7-c306-4b30-aa16-6128e2017225&numOfRows=10&pageNo=1"
try:
    res = requests.get(url, timeout=5)
    res.encoding = 'utf-8'
    root = ET.fromstring(res.text)
    items = root.findall('.//item')
    for item in items[:2]:
        print("--- ITEM ---")
        for child in item:
            print(f"{child.tag}: {child.text}")
except Exception as e:
    print(e)
