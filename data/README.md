# 데이터 설명

## 수집 데이터 (OpenAPI)

- **출처**: 로스트아크 OpenAPI `https://developer-lostark.game.smilegate.net`
- **수집 방식**: `collect.py` 1회 실행 + cron 기반 7분 간격 자동 수집
- **저장 포맷**: JSON (raw) -> Parquet (processed)
- **저장 경로**: 로컬 `data/raw/` -> HDFS `/user/maria_dev/auction/raw/`
- **처리 경로**: HDFS `/user/maria_dev/auction/processed/`

### 수집 대상 카테고리

| 카테고리 | 예시 아이템 |
|----------|-------------|
| 생활재료 | 들꽃, 목재, 철광석, 생선, 고대 유물 등 |
| 재련재료 | 오레하/아비도스 융화 재료, 돌파석, 수호석, 파괴석 계열 |
| 재련추가 | 별의 숨결, 달의 숨결, 태양의 은총/축복/가호, 빙하/용암의 숨결 |
| 유물각인서 | 주요 유물 각인서 40여 종 |
| 젬 | 혼돈/질서 젬 6종 |

## HDFS 디렉토리 구조

```text
/user/maria_dev/auction/raw/YYYY-MM-DD/HH/   # 수집 원본 JSON
/user/maria_dev/auction/processed/           # Spark 전처리 결과 (Parquet)
/user/maria_dev/auction/recipe/              # 레시피 CSV
```

## 스키마

### auction (수집 원본)

| 컬럼 | 타입 | 설명 |
|------|------|------|
| collected_at | TIMESTAMP | 수집 시각 |
| category | STRING | 카테고리 |
| item_name | STRING | 아이템 이름 |
| grade | STRING | 등급 |
| price | BIGINT | 현재 최저가 (골드) |
| quantity | INT | 수량 |
| end_date | STRING | 경매 종료 시각 |

### oreha_recipe.csv

| 컬럼 | 설명 |
|------|------|
| result_item | 제작 결과물 이름 |
| material_name | 필요 재료 이름 |
| quantity | 필요 수량 |
| craft_fee | 제작 수수료 (골드) |
| route | 제작 경로 |
| result_quantity | 1회 제작 산출 수량 |

## 주의

- 대용량 원본 데이터 전체는 GitHub에 올리지 않고, 저장소에는 샘플 raw 데이터만 포함
- 실제 누적 원본 데이터는 HDFS `/user/maria_dev/auction/raw/` 기준으로 관리
