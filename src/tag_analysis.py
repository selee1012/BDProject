from pyspark.sql import SparkSession
from pyspark.sql.functions import col, size, explode, collect_list
from pyspark.ml.feature import StopWordsRemover, Word2Vec, Normalizer
from pyspark.ml.clustering import KMeans

spark = SparkSession.builder.appName("tag_analysis2").enableHiveSupport().getOrCreate()
spark.sparkContext.setLogLevel("WARN")

df = spark.table("devto_articles").select("tags").where(size(col("tags")) > 1)

# 기술 스택이 아닌 용어들 제거
stop = ["webdev","beginners","discuss","tutorial","career","codenewbie",
        "watercooler","showdev","programming","productivity","news",
        "opensource","help","todayilearned","devjournal","writing"]
remover = StopWordsRemover(inputCol="tags", outputCol="clean_tags", stopWords=stop)
clean = remover.transform(df).where(size(col("clean_tags")) > 1)

# Word2Vec 학습
w2v = Word2Vec(vectorSize=50, minCount=5, seed=42, inputCol="clean_tags", outputCol="vec")
model = w2v.fit(clean)
vectors = model.getVectors()

# 추천 - 코사인 유사도
vocab = set(r["word"] for r in vectors.select("word").collect())
for q in ["react","typescript","docker","python","node","aws"]:
    if q in vocab:
        print("=== study-together for: " + q + " ===")
        model.findSynonyms(q, 8).show(truncate=False)

# 클러스터링 -> 이전에는 그냥 유클리디안 거리로 했다가 너무 거리가 먼 단어들은 혼자 남게 됨
# 1) 태그 빈도 계산 -> 상위 100개만
freq = clean.select(explode(col("clean_tags")).alias("word")).groupBy("word").count()
print("=== top 20 tags (trend) ===")
freq.orderBy(col("count").desc()).show(20, truncate=False)
top_tags = [r["word"] for r in freq.orderBy(col("count").desc()).limit(100).collect()]

# 2) 상위 태그 벡터만 골라 L2 정규화 (코사인 기준)
top_vecs = vectors.where(col("word").isin(top_tags))
top_vecs = Normalizer(inputCol="vector", outputCol="nvec", p=2.0).transform(top_vecs)

# 3) K-means
km = KMeans(k=8, seed=42, featuresCol="nvec", predictionCol="cluster")
km_model = km.fit(top_vecs)
clustered = km_model.transform(top_vecs)
print("=== tag clusters (top 100 tags, normalized) ===")
clustered.groupBy("cluster").agg(collect_list("word").alias("tags")).orderBy("cluster").show(truncate=False)

spark.stop()