import requests

keys = [
    "2e029955-4eab-4b1c-a67a-6096b2300fad",
    "967feea7-c306-4b30-aa16-6128e2017225"
]

def test_api():
    # Try different combinations of KCISA OpenAPI URLs
    for key in keys:
        print(f"--- Testing UUID as routing key: {key} ---")
        try:
            url = f"http://api.kcisa.kr/openapi/API_ROUTING_KEY/request?serviceKey={key}"
            res = requests.get(url, timeout=3)
            print("Status:", res.status_code)
            print("Body preview:", res.text[:200])
        except Exception as e:
            print("Error:", e)
         
if __name__ == "__main__":
    test_api()
