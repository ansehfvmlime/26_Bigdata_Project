# 데이터 설명

## 수집 데이터 (OpenAPI)

- **출처**: 로스트아크 OpenAPI `https://developer-lostark.game.smilegate.net`
- **수집 주기**: 2시간 간격 자동 수집
- **저장 포맷**: JSON (raw) → Parquet (processed)
- **예상 규모**: 아이템 30~50종 × 하루 12회 × 14일+ → 100MB+

### 수집 대상 아이템

| 카테고리 | 아이템 |
|----------|--------|
| 생활재료 | 빙하의 숨결, 수렵물, 채집물, 벌목물, 광물 |
| 오레하 | 오레하 융화 재료, 상급 오레하 융화 재료 |

## HDFS 디렉토리 구조

```
/data/auction/raw/YYYY-MM-DD/HH/   # 수집 원본 JSON
/data/auction/processed/            # Spark 전처리 결과 (Parquet)
/data/auction/recipe/               # 레시피 CSV
```

## 스키마

### auction (수집 원본)

| 컬럼 | 타입 | 설명 |
|------|------|------|
| collected_at | TIMESTAMP | 수집 시각 |
| category | STRING | 카테고리 (생활재료/오레하) |
| item_name | STRING | 아이템 이름 |
| grade | STRING | 등급 |
| price | BIGINT | 현재 최저가 (골드) |
| quantity | INT | 수량 |

### oreha_recipe.csv

| 컬럼 | 설명 |
|------|------|
| result_item | 제작 결과물 이름 |
| material_name | 필요 재료 이름 |
| quantity | 필요 수량 |
| craft_fee | 제작 수수료 (골드) |

## 주의

- `data/raw/`, `data/processed/` 는 `.gitignore` 처리 (용량 문제)
- `data/sample/` 에 샘플 100~1000줄만 커밋
