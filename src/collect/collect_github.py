import requests
import gzip
import json
import os
from datetime import datetime, timedelta

base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
data_dir = os.path.join(base_dir, "data")
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

DAYS = 3

f = open(os.path.join(data_dir, "github.jsonl"), "w", encoding="utf-8")
total = 0

for d in range(1, DAYS + 1):
    day = (datetime.utcnow() - timedelta(days=d)).strftime("%Y-%m-%d")
    for hour in range(24):
        url = "https://data.gharchive.org/" + day + "-" + str(hour) + ".json.gz"

        r = requests.get(url, stream=True)
        if r.status_code != 200:
            continue

        out = open("tmp.json.gz", "wb")
        for chunk in r.iter_content(chunk_size=1024 * 1024):
            out.write(chunk)
        out.close()

        gz = gzip.open("tmp.json.gz", "rt", encoding="utf-8")
        for line in gz:
            event = json.loads(line)
            if event["type"] == "WatchEvent":
                data = {
                    "type": event["type"],
                    "repo": event["repo"]["name"],
                    "created_at": event["created_at"]
                }
                f.write(json.dumps(data, ensure_ascii=False) + "\n")
                total += 1
        gz.close()

        os.remove("tmp.json.gz") # 디스크 문제로 인해 처리가 끝나면 바로 삭제

f.close()
print(str(total))