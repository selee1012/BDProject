from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StringType, LongType

spark = SparkSession.builder.appName("hn_stream_hdfs").getOrCreate()
spark.sparkContext.setLogLevel("WARN")

df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "sandbox-hdp.hortonworks.com:6667") \
    .option("subscribe", "hn-stream") \
    .option("startingOffsets", "earliest") \
    .load()

schema = StructType() \
    .add("id", LongType()) \
    .add("title", StringType()) \
    .add("score", LongType()) \
    .add("time", LongType())

parsed = df.select(from_json(col("value").cast("string"), schema).alias("d")).select("d.*")

# JSON으로 계속 저장
query = parsed.writeStream \
    .outputMode("append") \
    .format("json") \
    .option("path", "/tmp/hn_stream_out") \
    .option("checkpointLocation", "/tmp/hn_stream_ckpt") \
    .start()

query.awaitTermination()