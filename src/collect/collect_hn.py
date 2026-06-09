import requests
import json
import os

base = "https://hacker-news.firebaseio.com/v0/"
item_url = base + "item/"

base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
data_dir = os.path.join(base_dir, "data")
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

# 인기 + 최신 + 베스트 목록 합치기 -> 중복 제거
top = requests.get(base + "topstories.json").json()
new = requests.get(base + "newstories.json").json()
best = requests.get(base + "beststories.json").json()
ids = list(set(top + new + best))

f = open(os.path.join(data_dir, "hn.jsonl"), "w", encoding="utf-8")
count = 0

for story_id in ids:
    item = requests.get(item_url + str(story_id) + ".json").json()
    if item is None:
        continue
    data = {
        "id": item.get("id"),
        "title": item.get("title"),
        "score": item.get("score", 0),
        "comments": item.get("descendants", 0),
        "time": item.get("time"),
        "url": item.get("url", "")
    }
    f.write(json.dumps(data, ensure_ascii=False) + "\n")
    count += 1

f.close()
print(str(count))