# 데이터 설명 (data/)

수집한 원본 데이터는 한 줄에 JSON 객체 하나인 **JSON Lines(`.jsonl`)** 형식입니다.

- 전체 원본 데이터(`devto.jsonl`, `hn.jsonl`, `github.jsonl`)는 용량이 커서 git에 올리지 않습니다 (`.gitignore`).
- 대신 각 소스의 앞부분 100줄을 `*_sample.jsonl` 로 커밋
  (`devto_sample.jsonl`, `hn_sample.jsonl`, `github_sample.jsonl`).
- 전체 데이터는 `src/collect/` 의 수집 스크립트를 실행하면 다시 생성됩니다.

## 데이터 출처

| 소스 | 파일 | 출처 / API | 수집 방법 |
|---|---|---|---|
| dev.to | `devto.jsonl` | https://dev.to/api/articles | 기술 블로그 글과 태그를 페이지 단위로 수집 |
| Hacker News | `hn.jsonl` | https://hacker-news.firebaseio.com/v0/ | top/new/best 목록의 글을 item API로 수집 |
| GitHub Archive | `github.jsonl` | https://data.gharchive.org/ | 시간별 이벤트 덤프에서 `WatchEvent`(스타)만 추출 |

## 스키마

### devto.jsonl
| 필드 | 타입 | 설명 |
|---|---|---|
| id | int | dev.to 글 고유 ID |
| title | string | 글 제목 |
| tags | array&lt;string&gt; | 태그 목록 (예: `["kubernetes","ai"]`) |
| reactions | int | 긍정 반응 수 |
| comments | int | 댓글 수 |
| published_at | string | 발행 시각 (ISO 8601) |
| url | string | 글 URL |

```
{"id": 3711601, "title": "Seamless scaling with VPA In-place Pod Resize on GKE", "tags": ["kubernetes","ai","gke","googlecloud"], "reactions": 5, "comments": 0, "published_at": "2026-06-04T18:19:03Z", "url": "https://dev.to/..."}
```

### hn.jsonl
| 필드 | 타입 | 설명 |
|---|---|---|
| id | int | Hacker News 글 ID |
| title | string | 글 제목 |
| score | int | 점수(추천 수) |
| comments | int | 댓글 수 (HN의 descendants) |
| time | int | 작성 시각 (Unix epoch, 초) |
| url | string | 외부 링크 (없으면 빈 문자열) |

```
{"id": 48424960, "title": "120k Lines of Rust: Inside the Nosdesk Backend", "score": 40, "comments": 2, "time": 1780752856, "url": "https://..."}
```

### github.jsonl
| 필드 | 타입 | 설명 |
|---|---|---|
| type | string | 이벤트 종류 (항상 `"WatchEvent"` = 스타) |
| repo | string | 저장소 이름 (`"owner/name"` 형식) |
| created_at | string | 이벤트 시각 (ISO 8601) |

```
{"type": "WatchEvent", "repo": "skydiscover-ai/skydiscover", "created_at": "2026-06-07T01:43:54Z"}
```