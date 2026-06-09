CREATE EXTERNAL TABLE github_events (
  type       STRING,
  repo       STRING,
  created_at STRING
)
ROW FORMAT SERDE 'org.apache.hive.hcatalog.data.JsonSerDe'
STORED AS TEXTFILE
LOCATION '/tmp/github';

SELECT repo, COUNT(*) AS stars
FROM github_events
GROUP BY repo
ORDER BY stars DESC
LIMIT 20;