ADD JAR /usr/hdp/current/hive-webhcat/share/hcatalog/hive-hcatalog-core.jar;

CREATE EXTERNAL TABLE hn_stories (
  id       BIGINT,
  title    STRING,
  score    INT,
  comments INT,
  `time`   BIGINT,
  url      STRING
)
ROW FORMAT SERDE 'org.apache.hive.hcatalog.data.JsonSerDe'
STORED AS TEXTFILE
LOCATION '/tmp/hn';

SELECT title, score
FROM hn_stories
ORDER BY score DESC
LIMIT 20;