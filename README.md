# 기술 트렌드 자동 분류 및 분석 & 관련 기술 서칭 도우미 시스템

## 문제 정의
### - 풀고자 하는 문제 : 빠르게 변하는 기술 생태계의 어떤 분야가 떠오르고 있고 그 분야를 공부하고자 할 때 같이 어떤 분야를 공부해야 하는지 따라가기 어렵다. 이를 통해 최근 트렌디한 기술들을 찾아주고 그 기술을 공부하기 위해 같이 공부해야 하는 기술들을 추천해주는 프로젝트를 진행하고자 한다.
### - 데이터 수집 및 사용 : 기술 관련된 데이터들이 많이 모이는 GitHub Archive(실제 코드 활동: 레포 생성·스타·이슈), Hacker News API(커뮤니티 담론: 제목·코멘트), dev.to API(기술 블로그 글·태그) 등을 활용하고자 한다.

## 기술 스택
### - Python (requests, json, gzip) : GitHub Archive dump 다운로드 및 HN/dev.to API 호출 용도로 사용한다.
### - Kafka : 트렌드에 민감하기 때문에 HN 같은 실시간 데이터를 스트리밍으로 가져오기 위해 사용된다.
### - HDFS + Parquet : 수집한 원본 및 전처리 데이터를 영구 저장하는 용도로 사용한다.
### - Apache Spark (PySpark) : 전처리, 토큰화, 집계, 분석 쿼리에 활용한다.
### - Spark Streaming : Kafka에서 들어오는 HN 스트림의 실시간 데이터 처리(윈도우 집계)에 활용한다.
### - Spark MLlib : 기술 키워드 간의 임베딩 학습(Word2Vec), 클러스터링(K-means), 유사도 계산에 활용한다.
### - Apache Hive : 분석용 외부 테이블 정의 및 Spark SQL 백엔드로 활용한다.
### - Streamlit + Plotly : 카테고리 맵·트렌드 차트·추천 결과 시각화 대시보드로 활용한다.

## 구현 계획
### case1(배치 처리)
#### GitHub Archive, dev.to API → Python 수집 스크립트 → HDFS → Spark 전처리 → Hive 테이블

### case2(실시간 처리)
#### Hacker News API → Kafka → Spark Streaming → HDFS (윈도우 집계)

### 분석 단계
#### Hive 테이블 + 실시간 집계 결과 → Spark MLlib (Word2Vec 임베딩 + K-means 클러스터링 + 코사인 유사도) → Streamlit 대시보드
