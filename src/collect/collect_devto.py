import requests
import json
import os

url = "https://dev.to/api/articles"
pages = 20

base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
data_dir = os.path.join(base_dir, "data")
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

count = 0
f = open(os.path.join(data_dir, "devto.jsonl"), "w", encoding="utf-8")

for page in range(1, pages + 1):
    params = {"per_page": 1000, "page": page}
    response = requests.get(url, params=params)
    articles = response.json()

    if len(articles) == 0:
        break

    for article in articles:
        data = {
            "id": article["id"],
            "title": article["title"],
            "tags": article["tag_list"],
            "reactions": article["positive_reactions_count"],
            "comments": article["comments_count"],
            "published_at": article["published_at"],
            "url": article["url"]
        }
        f.write(json.dumps(data, ensure_ascii=False) + "\n")
        count += 1

f.close()
print(str(count))