#!/bin/bash
# 전체 파이프라인 자동 실행 (가산점)
# Usage: ./run_pipeline.sh
set -e

echo "========================================"
echo " 로스트아크 경매장 분석 파이프라인"
echo " $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================"

# 환경 확인
if [ -z "$LOSTARK_API_KEY" ]; then
    if [ -f .env ]; then
        export $(cat .env | xargs)
    else
        echo "[ERROR] .env 파일이 없습니다."
        echo "  cp .env.example .env 후 API 키를 입력하세요."
        exit 1
    fi
fi

# 1. 데이터 수집
echo ""
echo "[1/5] 데이터 수집..."
python src/ingest/collect.py

# 2. HDFS 적재
echo ""
echo "[2/5] HDFS 적재..."
bash src/pipeline/upload_hdfs.sh

# 3. Hive 테이블 초기화 (최초 1회)
echo ""
echo "[3/5] Hive 테이블 및 레시피 적재..."
hdfs dfs -mkdir -p /data/auction/recipe
hdfs dfs -put -f data/recipe/oreha_recipe.csv /data/auction/recipe/
hive -f infra/hive_schema.sql

# 4. Spark 전처리
echo ""
echo "[4/5] Spark 전처리..."
spark-submit src/pipeline/preprocess.py

# 5. 분석 실행
echo ""
echo "[5/5] 분석 실행..."
hive -f src/analyze/q1_daily_trend.sql
hive -f src/analyze/q2_craft_profit.sql
spark-submit src/analyze/q3_correlation.py
spark-submit src/analyze/q4_anomaly.py
python src/analyze/visualize.py

echo ""
echo "========================================"
echo " 완료! results/ 폴더에서 결과 확인"
echo "========================================"
