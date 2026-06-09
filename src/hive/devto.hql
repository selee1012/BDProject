ADD JAR /usr/hdp/current/hive-webhcat/share/hcatalog/hive-hcatalog-core.jar;

CREATE EXTERNAL TABLE devto_articles (
  id           BIGINT,
  title        STRING,
  tags         ARRAY<STRING>,
  reactions    INT,
  comments     INT,
  published_at STRING,
  url          STRING
)
ROW FORMAT SERDE 'org.apache.hive.hcatalog.data.JsonSerDe'
STORED AS TEXTFILE
LOCATION '/tmp/devto';

SELECT tag, COUNT(*) AS cnt
FROM devto_articles
LATERAL VIEW explode(tags) t AS tag
GROUP BY tag
ORDER BY cnt DESC
LIMIT 20;