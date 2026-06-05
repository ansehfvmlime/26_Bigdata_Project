빅데이터프로그래밍 기말 대체 프로젝트  
60211644 김민서

# 로스트아크 경매장 시세 분석 시스템

## 개요

온라인 게임 로스트아크 OpenAPI를 통해 게임 내 경매장 시세 데이터를 자동 수집하고,
Hadoop 기반 빅데이터 파이프라인(HDFS → Spark → Hive)으로 처리·분석하는 시스템.

레이드 초기화 주기(수요일)와 아이템 시세의 관계,
인게임 필수 아이템 제작과 구매 간 이득 분석,
요일 - 가격 상관관계,
유물각인서 이상치 탐지를 수행한다.

---

## 문제 정의

**Q1**: 요일별로 아이템 시세가 어떻게 변하는가? (레이드 초기화(수요일) 전후 비교)  
→ `GROUP BY day_of_week`, `AVG`, `MIN`, `MAX` (HiveQL)

**Q2**: 영지 제작 원가 vs 경매장 구매가 — 언제, 얼마나 이득인가?  
→ 레시피 `JOIN`, route별 최저 원가 계산, `profitable_pct` 파생 컬럼 (PySpark)

**Q3**: 요일과 재련재료/재련추가 가격 간 상관관계가 유의미한가?  
→ `corr(day_of_week, price)`, 아이템별 상관계수 분석 (PySpark)

**Q4**: 유물각인서 중 평균 시세 대비 비정상적으로 낮은 매물 패턴이 있는가?  
→ `STDDEV`, `AVG` 기반 이상치 탐지 (평균 - 2×표준편차 기준) (PySpark)

---

## 기술 스택

| 역할        | 기술                                                            |
| ----------- | --------------------------------------------------------------- |
| 데이터 수집 | Python (requests) — 로스트아크 OpenAPI 호출                     |
| 자동화      | Bash cron — 7분 간격 수집, 9분 간격 HDFS 적재                   |
| 분산 저장   | HDFS (HDP Sandbox on GCP)                                       |
| 전처리      | Apache Spark (PySpark) — DataFrame 정제, 레시피 JOIN, 원가 계산 |
| 분석        | Apache Hive (HiveQL) + PySpark — 집계, 상관분석, 이상치 탐지    |
| 시각화      | 인터랙티브 대시보드 (Chart.js 기반, 항목별 on/off 토글)         |

---

## 데이터 현황

- 수집 기간: 2026-05-20 ~ (자동 수집 진행 중)
- 수집 주기: 7분 간격 (cron)
- 수집 카테고리: 식물채집, 벌목, 채광, 수렵, 낚시, 고고학, 재련재료, 재련추가, 유물각인서, 젬 (10종)
- 처리된 레코드: auction_log 417,082건 / craft_profit 23,887건 (Parquet) - 2026/06/05 기준
- HDFS 누적 용량: 86.7MB (마감까지 ~100MB 달성 예정)

---

## Repository 구조

26_Bigdata_Project/
├── README.md
├── data/
│ ├── raw
│ ├── recipe/
│ │ └── oreha_recipe.csv # 오레하/아비도스 제작 레시피 (route, result_quantity 포함)
│ └── README.md # 아에템에 관한 간단한 설명
├── src/
│ ├── ingest/
│ │ ├── data
│ │ └── collect.py # OpenAPI 수집 스크립트 (429 오류 재시도 포함)
│ ├── pipeline/
│ │ ├── upload_hdfs.sh # HDFS 적재 스크립트
│ │ └── preprocess.py # Spark 전처리 (정제 + route별 최저 원가 계산)
│ └── analyze/
│ ├── q1_daily_trend.sql # Q1: 요일별 시세 분석 (HiveQL)
│ ├── q2_craft_profit.sql # Q2: 제작 이득 분석 (HiveQL)
│ ├── q3_correlation.py # Q3: 요일-가격 상관계수 분석 (PySpark)
│ ├── q4_anomaly.py # Q4: 유물각인서 이상치 탐지 (PySpark)
│ └── visualize.py
├── run_pipeline.sh
├── .env
├── .env.example
└── infra/
└── hive_schema.sql # Hive 외부 테이블 DDL

---

## 실행 환경

- HDP Sandbox 3.0.1 (Docker, GCP VM)
- Python 3.6
- Apache Spark 2.x (PySpark)
- Apache Hive 3.1
- HDFS

---

## 실행 방법

### 1. 환경 변수 설정

```bash
export LOSTARK_API_KEY="발급받은_API_키"
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
```

영구 설정은 `~/.zshrc` 또는 `~/.bashrc`에 추가:

```bash
echo 'export LOSTARK_API_KEY="발급받은_API_키"' >> ~/.zshrc
source ~/.zshrc
```

### 2. HDFS 디렉토리 및 레시피 적재

```bash
hdfs dfs -mkdir -p /user/maria_dev/auction/raw
hdfs dfs -mkdir -p /user/maria_dev/auction/processed
hdfs dfs -mkdir -p /user/maria_dev/auction/recipe
hdfs dfs -put data/recipe/oreha_recipe.csv /user/maria_dev/auction/recipe/
```

### 3. Hive 테이블 생성

```bash
hive -f infra/hive_schema.sql
```

### 4. 데이터 수집 (1회)

```bash
LOSTARK_API_KEY="키" python3.6 src/ingest/collect.py
```

### 5. HDFS 적재

```bash
bash src/pipeline/upload_hdfs.sh
```

### 6. Spark 전처리

```bash
spark-submit \
  --conf spark.yarn.appMasterEnv.PYSPARK_PYTHON=/bin/python3.6 \
  --driver-memory 512m \
  --executor-memory 512m \
  src/pipeline/preprocess.py
```

### 7. 분석 실행

```bash
# Q1: 요일별 시세 패턴 (Hive)
hive -f src/analyze/q1_daily_trend.sql

# Q2: 제작 이득 분석 (Spark)
spark-submit \
  --conf spark.yarn.appMasterEnv.PYSPARK_PYTHON=/bin/python3.6 \
  src/analyze/q3_correlation.py

# Q3: 요일-가격 상관관계 (Spark)
LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 spark-submit \
  --conf spark.yarn.appMasterEnv.PYSPARK_PYTHON=/bin/python3.6 \
  src/analyze/q3_correlation.py

# Q4: 유물각인서 이상치 탐지 (Spark)
LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 spark-submit \
  --conf spark.yarn.appMasterEnv.PYSPARK_PYTHON=/bin/python3.6 \
  src/analyze/q4_anomaly.py
```

### 8. 자동화 (cron 설정)

```bash
# 수집 7분 간격, HDFS 적재 9분 간격
*/7 * * * * cd /home/maria_dev/26_Bigdata_Project && LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 LOSTARK_API_KEY="키" python3.6 src/ingest/collect.py >> /home/maria_dev/collect.log 2>&1
*/9 * * * * cd /home/maria_dev/26_Bigdata_Project && bash src/pipeline/upload_hdfs.sh >> /home/maria_dev/upload.log 2>&1
```

---

## 주요 분석 결과

### Q1 — 요일별 시세 패턴

- 달의 숨결(재련추가): 수요일 188골드로 급등(+36%) → 레이드 초기화 직접 영향
- 재련재료: 토요일 최고(177골드), 화요일 최저(170골드)
- 유물각인서 고가 아이템: 수~목 하락, 토~일 상승 패턴

### Q2 — 제작 이득 분석

- 아비도스 융화 재료: 88~98% 이득 (목요일 98.1% 최고)
- 오레하 융화 재료: 목요일 76.2% vs 화요일 45.5% (요일별 차이 뚜렷)
- 최상급 오레하: 일요일 99.7% 이득 vs 목요일 42.5% 손해

### Q3 — 요일-가격 상관관계

- 카테고리 전체 상관계수는 거의 0 (재련재료 +0.0012, 재련추가 -0.0023)
- 개별 아이템: 정제된 파괴강석 -0.4119 (강한 음의 상관), 경이로운 명예의 돌파석 +0.3527 (강한 양의 상관)
- 재련추가: 수요일(4) 135골드 최저 → 레이드 초기화 영향 통계적 확인

### Q4 — 유물각인서 이상치 탐지

- 전체 114,243건 중 725건(0.63%) 이상치 탐지
- 덤핑 빈도 1위: 유물 아드레날린 각인서 90건 (평균가 대비 7.9% 할인)
- 덤핑 강도 1위: 유물 추진력 각인서 88.7% 할인
- 요일별: 목요일에 485건 집중(전체 66.9%) → Q1, Q2 결과와 일관된 패턴

---

## 참고 자료 및 AI 도구 사용

### 참고 자료

- [로스트아크 OpenAPI 개발자 포털](https://developer-lostark.game.smilegate.net)
- Apache Spark 공식 문서: https://spark.apache.org/docs/latest/
- Apache Hive 공식 문서: https://hive.apache.org/
- HDP Sandbox 강의 자료 (빅데이터프로그래밍, 2026)

### AI 도구 사용 내역

- Claude: 전체 파이프라인 설계 및 디버깅 보조, 코드 오류 수정, README 초안 작성
- GPT : 프로젝트 디버깅 및 시각화 Code 작성 보조
