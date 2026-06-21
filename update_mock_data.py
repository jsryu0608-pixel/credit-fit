import random
import re

# Seoul bounding box
# Lat: 37.45 ~ 37.65
# Lng: 126.80 ~ 127.15

districts = [
    "강남구", "강동구", "강북구", "강서구", "관악구", "광진구", "구로구", "금천구",
    "노원구", "도봉구", "동대문구", "동작구", "마포구", "서대문구", "서초구", "성동구",
    "성북구", "송파구", "양천구", "영등포구", "용산구", "은평구", "종로구", "중구", "중랑구"
]

sports_types = [
    "유소년 축구교실", "태권도장", "유도관", "검도교실", "복싱클럽", "어린이 수영장", 
    "탁구교실", "배드민턴 클럽", "주짓수 아카데미", "클라이밍 센터"
]

images = [
    "https://images.unsplash.com/photo-1555597673-b21d5c935865?auto=format&fit=crop&w=500&q=60", # taekwondo/martial arts
    "https://images.unsplash.com/photo-1588636187515-58589252c806?auto=format&fit=crop&w=500&q=60", # judo
    "https://images.unsplash.com/photo-1552079011-cb29528659d4?auto=format&fit=crop&w=500&q=60", # kendo/gym
    "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?auto=format&fit=crop&w=500&q=60", # boxing
    "https://images.unsplash.com/photo-1579952363873-27f3bade9f55?auto=format&fit=crop&w=500&q=60", # soccer
    "https://images.unsplash.com/photo-1519315901367-f34f9274ceb3?auto=format&fit=crop&w=500&q=60", # swimming
    "https://images.unsplash.com/photo-1511067007398-7e4b90cfa4bc?auto=format&fit=crop&w=500&q=60", # badminton/tennis
    "https://images.unsplash.com/photo-1563299796-b729d0af54a5?auto=format&fit=crop&w=500&q=60"  # climbing
]

facilities_data = []

for i in range(50):
    dist = random.choice(districts)
    stype = random.choice(sports_types)
    name = f"{dist} {random.choice(['튼튼', '열정', '국가대표', '청룡', '백호', '구립', '시립', '건강'])} {stype}"
    
    lat = round(random.uniform(37.45, 37.65), 5)
    lng = round(random.uniform(126.80, 127.15), 5)
    base_credit = random.randint(2, 6)
    img = random.choice(images)
    
    fac = f'        {{"id": "VCH{i+1:03d}", "name": "{name}", "lat": {lat}, "lng": {lng}, "base_credit": {base_credit}, "is_public": True, "image": "{img}"}}'
    facilities_data.append(fac)

new_data_str = "    facilities_data = [\n" + ",\n".join(facilities_data) + "\n    ]"

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

# Replace the existing facilities_data array in app.py
pattern = r"facilities_data\s*=\s*\[.*?\]"
content = re.sub(pattern, new_data_str, content, flags=re.DOTALL)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Successfully injected 50 mock facilities into app.py")
