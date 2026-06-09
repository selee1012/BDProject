# 기술 트렌드 자동 분류·분석 및 함께 공부할 기술 추천 시스템
명지대학교 빅데이터프로그래밍(2026-1) 기말 프로젝트

## 1. 프로젝트 개요 (Overview)

### 분석 배경
기술 생태계는 빠르게 변해서, 지금 어떤 기술이 떠오르는지 그리고 특정 기술을 공부할 때 함께 공부하면 좋은 기술이 무엇인지 따라가기 어렵다.
여러 기술 커뮤니티의 데이터를 모아 트렌드를 자동으로 집계하고, 함께 등장하는 기술을 추천해주는 시스템을 만든다.

### 핵심 질문
- **트렌드**: 최근 기술 글에서 가장 많이 언급되는 기술(태그)은 무엇인가?
- **추천**: 특정 기술을 공부할 때 함께 공부하면 좋은 기술은 무엇인가?
- **분류**: 비슷한 맥락에서 함께 쓰이는 기술끼리는 어떻게 묶이는가?

### 접근 방법
- dev.to 글의 태그 목록을 "문장"처럼 보고 **Word2Vec**으로 기술 임베딩을 학습
- **K-means**로 기술을 카테고리(군집)로 자동 분류
- **코사인 유사도(`findSynonyms`)**로 "함께 공부할 기술"을 추천
- Hacker News는 **Kafka + Spark Streaming**으로 실시간 수집

## 2. 데이터 소스 (Data Sources)

| 소스 | 내용 | 수집 방법 |
|---|---|---|
| dev.to API | 기술 블로그 글 + 태그 | `/api/articles` 페이지 단위 수집 (배치) |
| Hacker News API | 커뮤니티 글(제목·점수·댓글) | top/new/best 목록 + item API, 실시간은 Kafka |
| GitHub Archive | 스타(`WatchEvent`) 이벤트 | 시간별 `.json.gz` 덤프에서 추출 (최근 3일치) |

## 3. 기술 스택 (Tech Stack)

| 계층 | 도구 |
|---|---|
| 데이터 수집 | Python (requests, gzip, json) |
| 실시간 수집 | Apache Kafka |
| 분산 스토리지 | Apache HDFS (Hadoop) |
| 분산 처리 | Apache Spark (PySpark) |
| 실시간 처리 | Spark Streaming |
| 머신러닝 | Spark MLlib (Word2Vec, K-means, 코사인 유사도) |
| 데이터 웨어하우스 | Apache Hive (HQL, 외부 테이블) |
| 시각화 | Streamlit + Plotly |
| 인프라 | GCP VM, HDP Sandbox (Docker) |

## 4. 파이프라인 (Pipeline)

```
[배치] dev.to · GitHub Archive
──────────────────────────────────────
수집 스크립트 (Python)  →  data/*.jsonl
        │  hdfs dfs -put
        ▼
HDFS (/tmp/devto, /tmp/github)
        │  Hive 외부 테이블 (JsonSerDe)
        ▼
Hive 집계 (태그 상위 N · 스타 많은 레포 상위 N)


[실시간] Hacker News API
──────────────────────────────────────
hn_producer.py  →  Kafka (topic: hn-stream)
        │  Spark Streaming
        ▼
hn_stream.py  →  HDFS (/tmp/hn_stream_out) 적재


[분석] dev.to 태그  →  Spark MLlib
──────────────────────────────────────
HDFS (/tmp/devto)
        ▼
  · Word2Vec   : 태그 임베딩 학습
  · K-means    : 기술 카테고리 군집화
  · 코사인 유사도 : 함께 공부할 기술 추천
        │
        ▼
data/dashboard_data.json  →  Streamlit 대시보드
```

## 5. 실행 방법 (How to Run)

### 사전 준비
```
pip install requests kafka-python streamlit plotly pandas
```

### Step 1. 배치 전체 실행 (HDP Sandbox)
수집 → HDFS 적재 → Hive 집계 → 분석 → 대시보드 데이터 생성까지 한 번에 실행한다.
```
bash infra/run.sh
```

### Step 2. 실시간 파이프라인 (선택, 터미널 2개)
```
# 터미널 A: 프로듀서
python3.6 src/kafka/hn_producer.py

# 터미널 B: 스트리밍 소비 -> HDFS
spark-submit --master local[2] \
  --jars /usr/hdp/current/kafka-broker/libs/spark-sql-kafka-0-10_2.11-2.3.1.jar,/usr/hdp/current/kafka-broker/libs/kafka-clients-1.1.1.3.0.1.0-187.jar \
  src/kafka/hn_stream.py
```

### Step 3. 대시보드 (로컬 PC)
`data/dashboard_data.json`을 로컬 `data/`에 둔 뒤 실행한다.
```
python -m streamlit run analyze/app.py
```

## 6. 결과 요약 (Results)

> 아래 수치는 한 차례 실행 기준 예시이며, 수집 시점에 따라 달라진다.

- **데이터 규모**: dev.to 글 약 18,000건(태그 2개 이상), 학습된 기술 태그 약 650개
- **트렌드 상위**: `javascript` > `react` > `ai` > `css` > `python` …
- **추천 예시**
    - `docker` → kubernetes, aws, devops
    - `typescript` → vue, express, graphql
    - `react` → angular, npm
- **카테고리(군집)**: 프론트엔드 / 데브옵스 / AI·ML / 데이터·백엔드 등으로 자동 분류

### 결과물
| 파일 | 내용 |
|---|---|
| `data/dashboard_data.json` | 트렌드·군집·추천 결과 (대시보드 입력 데이터) |
| `analyze/app.py` (대시보드) | 트렌드 막대그래프 · 기술 카테고리 · 함께 공부할 기술 탭 |

## 7. 디렉터리 구조

```
BDProject/
├── README.md
├── data/
│   ├── Readme.MD                # 데이터 출처·스키마
│   ├── *_sample.jsonl           # 소스별 샘플 100줄 (전체 데이터는 .gitignore)
│   └── dashboard_data.json      # 분석 결과 (대시보드 입력)
├── src/
│   ├── collect/                 # 데이터 수집
│   │   ├── collect_devto.py
│   │   ├── collect_hn.py
│   │   └── collect_github.py
│   ├── hive/                    # Hive 외부 테이블 + 집계 (HQL)
│   │   ├── devto.hql
│   │   ├── hn.hql
│   │   └── github.hql
│   └── kafka/                   # 실시간 (Kafka + Spark Streaming)
│       ├── hn_producer.py
│       └── hn_stream.py
├── analyze/                     # 분석 + 대시보드
│   ├── tag_analysis.py          # Word2Vec + K-means (콘솔 확인용)
│   ├── export_results.py        # 분석 결과 -> dashboard_data.json
│   └── app.py                   # Streamlit 대시보드
└── infra/
    └── run.sh                   # 배치 전체 실행
```

## 8. AI Tool Usage
- **Claude (Claude Code)** : 코드 디버깅(*.py, *.hql, *.sh), Readme.md 및 보고서 내용 정리(초안은 본인이 작성), 초기 아키텍처 제안
- **ChatGPT** : 기술 문서 번역
