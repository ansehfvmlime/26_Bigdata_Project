빅데이터프로그래밍 기말 대체 프로젝트
60211644 김민서

# 로스트아크 경매장 시세 분석 시스템

## 개요

로스트아크 OpenAPI를 통해 경매장 시세 데이터를 수집하고,
Hadoop 기반 빅데이터 파이프라인으로 처리·분석하는 시스템

생활 재료(수렵물, 채집물 등)와 오레하(강화재료) 간의 가격 관계를 분석하여,
생활 재료를 통한 강화 재료 제작이 경매장 직접 구매보다 이득인지 판단하는 기능을 구현

## 문제 정의

Q1: 요일/시간대별로 아이템 시세가 어떻게 변하는가? (레이드 초기화 전후 비교)
`GROUP BY`, `AVG`, `MIN`

Q2: 영지 제작 원가 vs 경매장 구매가 — 언제, 얼마나 이득인가?
`JOIN`, 파생 컬럼(`profit`)

Q3: 생활 재료들 간 가격은 서로 동조화되어 움직이는가?
`JOIN`, `corr()` : 상관관계 분석

Q4: 평균 시세 대비 비정상적으로 낮은 가격의 매물이 올라오는 패턴이 있는가?
`STDDEV`, `AVG` : 이상치 탐지

---

## 예상 기술 스택

수집 Python (requests) — OpenAPI 호출 및 자동화
저장 HDFS — 분산 파일 시스템
전처리 Apache Spark (PySpark) — DataFrame 정제 및 원가 계산 JOIN
분석 Apache Hive (HiveQL) — SQL 기반 집계 분석
시각화 Matplotlib, Seaborn — 결과 그래프 생성
자동화 Bash Shell Script — 전체 파이프라인 일괄 실행

## Repository 구조

```
26_Bigdata_Project/
├── README.md
├── .env.example                        # API 키 템플릿 (실제 키는 .env에 보관)
├── run_pipeline.sh                     # 전체 파이프라인 자동 실행
├── data/
│   ├── README.md                       # 데이터 출처 및 스키마 설명
│   ├── recipe/
│   │   └── oreha_recipe.csv            # 오레하 제작 레시피
│   └── sample/                         # 샘플 데이터 (100~1000줄)
├── src/
│   ├── ingest/
│   │   └── collect.py                  # OpenAPI 수집 스크립트
│   ├── pipeline/
│   │   ├── upload_hdfs.sh              # HDFS 적재 스크립트
│   │   └── preprocess.py               # Spark 전처리 (정제 + 원가 계산)
│   └── analyze/
│       ├── q1_daily_trend.sql          # Q1: 요일별 시세 분석
│       ├── q2_craft_profit.sql         # Q2: 제작 이득 분석
│       ├── q3_correlation.py           # Q3: 재료 간 상관분석
│       ├── q4_anomaly.py               # Q4: 이상치 탐지
│       └── visualize.py                # 결과 시각화
└── infra/
    └── hive_schema.sql                 # Hive 테이블 DDL
```

## 구현 계획

### 사전 조건

- HDP Sandbox 구동 중
- 로스트아크 OpenAPI 키 발급
  ([개발자 포털](https://developer-lostark.game.smilegate.net))
- Python 3.x, PySpark, Hive 사용 가능 환경

### 환경 설정

```bash
# API 키 설정
cp .env.example .env
# .env 파일 열어서 실제 키 입력

# Python 패키지 설치
pip install requests python-dotenv
```

### 단계별 실행

```bash
# 1. HDFS 디렉토리 생성 및 레시피 적재
hdfs dfs -mkdir -p /data/auction/raw
hdfs dfs -mkdir -p /data/auction/processed
hdfs dfs -mkdir -p /data/auction/recipe
hdfs dfs -put data/recipe/oreha_recipe.csv /data/auction/recipe/

# 2. Hive 테이블 생성
hive -f infra/hive_schema.sql

# 3. 데이터 수집 (1회)
python src/ingest/collect.py

# 4. HDFS 적재
bash src/pipeline/upload_hdfs.sh

# 5. Spark 전처리
spark-submit src/pipeline/preprocess.py

# 6. 분석 실행
hive -f src/analyze/q1_daily_trend.sql
hive -f src/analyze/q2_craft_profit.sql
spark-submit src/analyze/q3_correlation.py
spark-submit src/analyze/q4_anomaly.py

# 7. 시각화
python src/analyze/visualize.py
```

### 전체 자동 실행

```bash
chmod +x run_pipeline.sh
./run_pipeline.sh
```

---

## 예상 결과물

- **Q1**: 요일별 아이템 평균 시세 라인 차트
- **Q2**: 요일 × 시간대 제작 이득 히트맵
- **Q3**: 생활재료 간 가격 상관관계 히트맵
- **Q4**: 이상치 매물 탐지 결과 및 덤핑 발생 빈도 분석

## AI 도구 사용 내역

- Claude: 예상 파이프라인 설계, README 초안 작성
