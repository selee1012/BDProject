import json
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, size, explode
from pyspark.ml.feature import StopWordsRemover, Word2Vec, Normalizer
from pyspark.ml.clustering import KMeans
import os

spark = SparkSession.builder.appName("export").enableHiveSupport().getOrCreate()
spark.sparkContext.setLogLevel("WARN")

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path = os.path.join(base_dir, "data", "dashboard_data.json")
with open(path, "r", encoding="utf-8") as f:
    df = json.load(f)
stop = ["webdev","beginners","discuss","tutorial","career","codenewbie",
        "watercooler","showdev","programming","productivity","news",
        "opensource","help","todayilearned","devjournal","writing"]
remover = StopWordsRemover(inputCol="tags", outputCol="clean_tags", stopWords=stop)
clean = remover.transform(df).where(size(col("clean_tags")) > 1)

w2v = Word2Vec(vectorSize=50, minCount=5, seed=42, inputCol="clean_tags", outputCol="vec")
model = w2v.fit(clean)
vectors = model.getVectors()
vocab = set(r["word"] for r in vectors.select("word").collect())

# 빈도수 상위 100
freq = clean.select(explode(col("clean_tags")).alias("word")).groupBy("word").count()
freq_rows = freq.orderBy(col("count").desc()).limit(100).collect()
top_tags = [r["word"] for r in freq_rows]
top_set = set(top_tags)
trend = [{"tag": r["word"], "count": int(r["count"])} for r in freq_rows[:30]]

# 클러스터링 - 상위 100 태그
top_vecs = vectors.where(col("word").isin(top_tags))
top_vecs = Normalizer(inputCol="vector", outputCol="nvec", p=2.0).transform(top_vecs)
km = KMeans(k=8, seed=42, featuresCol="nvec", predictionCol="cluster")
km_model = km.fit(top_vecs)
crows = km_model.transform(top_vecs).select("word", "cluster").collect()
clusters = [{"tag": r["word"], "cluster": int(r["cluster"])} for r in crows]

# 추천 - 상위 40 태그, 같은 상위태그 안에서만 6개
recommend = {}
for t in top_tags[:40]:
    if t in vocab:
        syn = model.findSynonyms(t, 20).collect()
        rec = [[r["word"], round(float(r["similarity"]), 3)] for r in syn if r["word"] in top_set][:6]
        recommend[t] = rec

out = {"trend": trend, "clusters": clusters, "recommend": recommend}
with open("dashboard_data.json", "w") as f:
    json.dump(out, f, ensure_ascii=True)
print("WROTE dashboard_data.json")
spark.stop()