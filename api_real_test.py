import requests
import xml.etree.ElementTree as ET

urls = [
    ("http://api.kcisa.kr/openapi/service/rest/meta2018/getKSPD0720184", "2e029955-4eab-4b1c-a67a-6096b2300fad"),
    ("http://api.kcisa.kr/openapi/service/rest/meta12/getKSCD0802", "967feea7-c306-4b30-aa16-6128e2017225")
]

for url, key in urls:
    full_url = f"{url}?serviceKey={key}&numOfRows=5&pageNo=1"
    print(f"Testing {url} ...")
    try:
        res = requests.get(full_url, timeout=10)
        print("Status:", res.status_code)
        
        # Try to parse XML
        try:
            root = ET.fromstring(res.content)
            items = root.findall('.//item')
            print(f"Found {len(items)} items.")
            for item in items:
                # print all child tags to see schema
                tags = {child.tag: child.text for child in item}
                print(tags)
        except Exception as parse_err:
            print("Parse Error:", parse_err)
            print("Response:", res.text[:500])
            
    except Exception as e:
        print("Error:", e)
    
    print("-" * 50)
