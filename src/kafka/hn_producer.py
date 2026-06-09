from kafka import KafkaProducer
import requests
import json
import time

# 포트는 6667
producer = KafkaProducer(
    bootstrap_servers="localhost:6667",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

base = "https://hacker-news.firebaseio.com/v0/"
seen = set()   # 중복 방지

print("streaming HN new stories... (Ctrl+C to stop)")
while True:
    ids = requests.get(base + "newstories.json").json()
    for story_id in ids[:30]: # 30개씩
        if story_id in seen:
            continue
        seen.add(story_id)
        item = requests.get(base + "item/" + str(story_id) + ".json").json()
        if item is None:
            continue
        data = {
            "id": item.get("id"),
            "title": item.get("title"),
            "score": item.get("score", 0),
            "time": item.get("time")
        }
        producer.send("hn-stream", data)
        print("sent id " + str(data["id"]))
    producer.flush()
    time.sleep(10)   # 10초마다