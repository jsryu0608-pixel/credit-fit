import os
import datetime
import random
import re
import requests
import xml.etree.ElementTree as ET
from flask import Flask, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    load_dotenv(override=True)
    return render_template('index.html')

def get_coords_for_name(name):
    if "올림픽" in name and "수영" in name:
        return (37.5218, 127.1239)
    if "올림픽" in name:
        return (37.5205, 127.1205)
    if "분당" in name:
        return (37.3827, 127.1189)
    if "일산" in name:
        return (37.6601, 126.7668)
    if "광명" in name or "스피돔" in name:
        return (37.4781, 126.8833)
    if "미사" in name or "경정" in name:
        return (37.5641, 127.1906)
    return (round(random.uniform(37.45, 37.65), 5), round(random.uniform(126.80, 127.15), 5))

# 실제 위치 기반의 서울/경기 공공/민간 체육시설 목업 데이터 46개 (API 데이터 부족분 보충용)
REAL_MOCK_CENTERS = [
    {"name": "성동구민종합체육센터", "lat": 37.5475, "lng": 127.0435},
    {"name": "마포구민체육센터", "lat": 37.5583, "lng": 126.8953},
    {"name": "서대문문화체육회관", "lat": 37.5855, "lng": 126.9360},
    {"name": "용산구문화체육센터", "lat": 37.5386, "lng": 126.9687},
    {"name": "강남구민체육관", "lat": 37.4930, "lng": 127.0650},
    {"name": "송파구체육문화회관", "lat": 37.4984, "lng": 127.1429},
    {"name": "강동구민회관", "lat": 37.5450, "lng": 127.1420},
    {"name": "노원구민체육센터", "lat": 37.6350, "lng": 127.0720},
    {"name": "도봉동실내스포츠센터", "lat": 37.6790, "lng": 127.0450},
    {"name": "강북구민운동장", "lat": 37.6330, "lng": 127.0200},
    {"name": "은평구민체육센터", "lat": 37.6360, "lng": 126.9200},
    {"name": "종로구민회관", "lat": 37.5740, "lng": 127.0150},
    {"name": "중구구민회관", "lat": 37.5660, "lng": 127.0010},
    {"name": "동대문구체육관", "lat": 37.5750, "lng": 127.0650},
    {"name": "중랑구민체육센터", "lat": 37.6080, "lng": 127.0900},
    {"name": "광진구민체육센터", "lat": 37.5400, "lng": 127.0950},
    {"name": "성북구민체육관", "lat": 37.5950, "lng": 127.0350},
    {"name": "동작구민체육센터", "lat": 37.4950, "lng": 126.9250},
    {"name": "관악구민종합체육센터", "lat": 37.4720, "lng": 126.9500},
    {"name": "금천구민문화체육센터", "lat": 37.4580, "lng": 126.9020},
    {"name": "구로구민체육센터", "lat": 37.4980, "lng": 126.8600},
    {"name": "양천구민체육센터", "lat": 37.5250, "lng": 126.8650},
    {"name": "강서구민올림픽체육센터", "lat": 37.5550, "lng": 126.8500},
    {"name": "영등포스포츠센터", "lat": 37.5180, "lng": 126.9100},
    {"name": "서초구민체육센터", "lat": 37.4950, "lng": 127.0010},
    {"name": "관악시민운동장", "lat": 37.4650, "lng": 126.9400},
    {"name": "마포창전스포츠센터", "lat": 37.5480, "lng": 126.9250},
    {"name": "상암월드컵경기장 수영장", "lat": 37.5680, "lng": 126.8970},
    {"name": "장충체육관", "lat": 37.5580, "lng": 127.0060},
    {"name": "고척스카이돔 체육시설", "lat": 37.4980, "lng": 126.8670},
    {"name": "잠실종합운동장 수영장", "lat": 37.5130, "lng": 127.0730},
    {"name": "효창운동장", "lat": 37.5420, "lng": 126.9600},
    {"name": "창동문화체육센터", "lat": 37.6530, "lng": 127.0500},
    {"name": "보라매공원 체육관", "lat": 37.4920, "lng": 126.9200},
    {"name": "남산타운 체육시설", "lat": 37.5500, "lng": 127.0080},
    {"name": "양재시민의숲 테니스장", "lat": 37.4700, "lng": 127.0350},
    {"name": "여의도공원 스포츠센터", "lat": 37.5250, "lng": 126.9200},
    {"name": "반포종합운동장", "lat": 37.5020, "lng": 126.9950},
    {"name": "한강시민공원 수영장(잠원)", "lat": 37.5250, "lng": 127.0150},
    {"name": "보라매청소년수련관", "lat": 37.4960, "lng": 126.9250},
    {"name": "도림동 다목적체육관", "lat": 37.5080, "lng": 126.8980},
    {"name": "망원유수지 체육공원", "lat": 37.5550, "lng": 126.8950},
    {"name": "양천장애인종합복지관", "lat": 37.5200, "lng": 126.8550},
    {"name": "성북레포츠타운", "lat": 37.6050, "lng": 127.0450},
    {"name": "아현스포렉스", "lat": 37.5550, "lng": 126.9550},
    {"name": "구로구로거리공원 체육관", "lat": 37.4950, "lng": 126.8900}
]

IMAGES = [
    "https://images.unsplash.com/photo-1519315901367-f34f9274ceb3?auto=format&fit=crop&w=500&q=60",
    "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?auto=format&fit=crop&w=500&q=60",
    "https://images.unsplash.com/photo-1511067007398-7e4b90cfa4bc?auto=format&fit=crop&w=500&q=60",
    "https://images.unsplash.com/photo-1552079011-cb29528659d4?auto=format&fit=crop&w=500&q=60",
]

@app.route('/api/facilities', methods=['GET'])
def get_facilities():
    center_api_key = os.getenv("CULTURE_CENTER_API_KEY")
    facilities_data = []
    seen_names = set()
    
    try:
        url = f"http://api.kcisa.kr/openapi/service/rest/meta12/getKSCD0802?serviceKey={center_api_key}&numOfRows=300&pageNo=1"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        items = root.findall('.//item')
        
        for idx, item in enumerate(items):
            title_elem = item.find('title')
            if title_elem is None or not title_elem.text:
                continue
                
            raw_title = title_elem.text.strip()
            clean_name = re.sub(r'(월회원|일일입장|일일|자유수영|\d+월|\d+일|회원|강습|반).*', '', raw_title).strip()
            
            if not clean_name:
                continue
                
            if clean_name in seen_names:
                continue
            seen_names.add(clean_name)
            
            lat, lng = get_coords_for_name(clean_name)
            base_credit = random.randint(2, 6)
            
            facilities_data.append({
                "id": f"API{idx:03d}",
                "name": clean_name,
                "lat": lat,
                "lng": lng,
                "base_credit": base_credit,
                "is_public": True,
                "image": random.choice(IMAGES)
            })
            
    except Exception as e:
        print(f"API Fetch failed: {e}. Moving on to augment mock data.")
        pass

    # API에서 긁어온 데이터가 부족하다면, 실제 위치 기반 목업 데이터로 50개까지 꽉 채움
    idx_counter = len(facilities_data)
    for mock_center in REAL_MOCK_CENTERS:
        if len(facilities_data) >= 50:
            break
            
        if mock_center["name"] in seen_names:
            continue
            
        facilities_data.append({
            "id": f"RL{idx_counter:03d}",
            "name": mock_center["name"],
            "lat": mock_center["lat"],
            "lng": mock_center["lng"],
            "base_credit": random.randint(2, 6),
            "is_public": True,
            "image": random.choice(IMAGES)
        })
        idx_counter += 1
    
    current_hour = datetime.datetime.now().hour
    processed_results = []
    
    for fac in facilities_data:
        is_peak_time = 18 <= current_hour <= 20
        
        if is_peak_time:
            predicted_congestion = 90
            final_credit = fac["base_credit"] + 2
            status = "혼잡"
        elif 12 <= current_hour <= 14:
            predicted_congestion = 65
            final_credit = fac["base_credit"]
            status = "보통"
        else:
            predicted_congestion = 30
            final_credit = max(1, fac["base_credit"] - 1)
            status = "쾌적"
            
        processed_results.append({
            "facility_id": fac["id"],
            "facility_name": fac["name"],
            "latitude": fac["lat"],
            "longitude": fac["lng"],
            "is_public": fac["is_public"],
            "predicted_congestion": predicted_congestion,
            "required_credit": final_credit,
            "status_message": status,
            "image": fac["image"]
        })
        
    return jsonify({
        "success": True,
        "data": processed_results,
        "current_hour": current_hour
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
