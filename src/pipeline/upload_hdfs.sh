#!/bin/bash
# HDFS 적재 스크립트
# Usage: bash src/pipeline/upload_hdfs.sh [날짜: YYYY-MM-DD]

DATE=${1:-$(date +%Y-%m-%d)}
LOCAL_DIR="data/raw/${DATE}"
HDFS_DIR="/data/auction/raw/${DATE}"

if [ ! -d "$LOCAL_DIR" ]; then
    echo "[ERROR] 로컬 디렉토리 없음: $LOCAL_DIR"
    echo "  먼저 collect.py를 실행해주세요."
    exit 1
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] HDFS 적재 시작: $DATE"
hdfs dfs -mkdir -p "$HDFS_DIR"
hdfs dfs -put -f "$LOCAL_DIR"/* "$HDFS_DIR"/
echo "[완료] $LOCAL_DIR → $HDFS_DIR"
