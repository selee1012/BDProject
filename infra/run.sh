#!/bin/bash
# =============================================================
# 배치 파이프라인 전체 실행 (GCP HDP 샌드박스 안에서)
#   사용법:  bash infra/run.sh
#
# 흐름: 수집 -> HDFS 적재 -> Hive 테이블/집계 -> 분석 -> 대시보드 데이터
# 실시간(Kafka)은 계속 떠 있어야 해서 따로 실행합니다 (맨 아래 참고)
# =============================================================
set -e

# 이 스크립트(infra/)에서 프로젝트 루트로 이동
cd "$(dirname "$0")/.."

echo "===== 0. 수집용 패키지 준비 ====="
python3.6 -m pip install --user requests >/dev/null 2>&1 || true

echo "===== 1. 데이터 수집 (GitHub Archive 다운로드라 오래 걸림) ====="
python3.6 src/collect/collect_devto.py
python3.6 src/collect/collect_hn.py
python3.6 src/collect/collect_github.py

echo "===== 2. HDFS 적재 ====="
hdfs dfs -mkdir -p /tmp/devto /tmp/hn /tmp/github
hdfs dfs -put -f data/devto.jsonl  /tmp/devto/
hdfs dfs -put -f data/hn.jsonl     /tmp/hn/
hdfs dfs -put -f data/github.jsonl /tmp/github/

echo "===== 3. Hive 외부 테이블 생성 + 집계 ====="
hive -f src/hive/devto.hql
hive -f src/hive/hn.hql
hive -f src/hive/github.hql

echo "===== 4. 분석 (Word2Vec + K-means) ====="
PYSPARK_PYTHON=python3.6 PYSPARK_DRIVER_PYTHON=python3.6 PYTHONIOENCODING=utf8 \
  spark-submit --master local[2] --driver-memory 1g analyze/tag_analysis.py

echo "===== 5. 대시보드 데이터 생성 (data/dashboard_data.json) ====="
PYSPARK_PYTHON=python3.6 PYSPARK_DRIVER_PYTHON=python3.6 PYTHONIOENCODING=utf8 \
  spark-submit --master local[2] --driver-memory 1g analyze/export_results.py

echo ""
echo "===== 배치 완료! ====="
echo "대시보드: 로컬 PC에서  python -m streamlit run analyze/app.py"
echo "         (data/dashboard_data.json 을 로컬 data/ 에 두고 실행)"

# =============================================================
# [실시간(Kafka) 파이프라인 - 따로 실행, 터미널 2개]
#
#  # (한 번만) 토픽 생성 - 자동생성이 꺼져 있을 때만
#  /usr/hdp/current/kafka-broker/bin/kafka-topics.sh --create \
#    --zookeeper sandbox-hdp.hortonworks.com:2181 \
#    --topic hn-stream --partitions 1 --replication-factor 1
#
#  # 터미널 A: 프로듀서 (kafka-python 필요)
#  python3.6 -m pip install --user kafka-python
#  python3.6 src/kafka/hn_producer.py
#
#  # 터미널 B: 스트리밍 소비 -> HDFS
#  spark-submit --master local[2] \
#    --jars /usr/hdp/current/kafka-broker/libs/spark-sql-kafka-0-10_2.11-2.3.1.jar,/usr/hdp/current/kafka-broker/libs/kafka-clients-1.1.1.3.0.1.0-187.jar \
#    src/kafka/hn_stream.py
# =============================================================