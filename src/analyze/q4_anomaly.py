"""
Q4: 경매장 이상치(덤핑) 탐지
"평균 시세 대비 비정상적으로 낮은 가격의 매물 패턴이 있는가?"
기준: 평균가 - 2 × 표준편차 이하 → 이상치로 분류
Usage:
    spark-submit src/analyze/q4_anomaly.py
"""

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = SparkSession.builder \
    .appName("LostArk_Q4_Anomaly") \
    .enableHiveSupport() \
    .getOrCreate()
spark.sparkContext.setLogLevel("WARN")

HDFS_PROCESSED = "hdfs:///data/auction/processed/auction_log/"

df = spark.read.parquet(HDFS_PROCESSED)

# ── 아이템별 평균 / 표준편차 계산 ─────────────────────────────────────────────
df_stats = df.groupBy("item_name") \
    .agg(
        F.avg("price").alias("avg_price"),
        F.stddev("price").alias("std_price"),
        F.count("*").alias("total_count")
    )

# ── 이상치 기준: 평균 - 2×표준편차 이하 ──────────────────────────────────────
df_with_stats = df.join(df_stats, on="item_name", how="inner") \
    .withColumn("lower_bound", F.col("avg_price") - 2 * F.col("std_price")) \
    .withColumn("is_anomaly", F.col("price") < F.col("lower_bound")) \
    .withColumn(
        "discount_pct",
        F.round((1 - F.col("price") / F.col("avg_price")) * 100, 1)
    )

df_anomaly = df_with_stats.filter(F.col("is_anomaly") == True)

# ── 결과 출력 ─────────────────────────────────────────────────────────────────
print("\n[Q4] 이상치 탐지 결과 (덤핑 의심 매물)")
print("-" * 60)
print(f"  전체 레코드: {df.count()}건")
print(f"  이상치 탐지: {df_anomaly.count()}건")

print("\n[아이템별 이상치 발생 빈도]")
df_anomaly.groupBy("item_name") \
    .agg(
        F.count("*").alias("anomaly_count"),
        F.round(F.avg("discount_pct"), 1).alias("avg_discount_pct"),
        F.round(F.min("price"), 0).alias("min_anomaly_price")
    ) \
    .orderBy(F.desc("anomaly_count")) \
    .show(truncate=False)

# ── 저장 ─────────────────────────────────────────────────────────────────────
df_anomaly.write.mode("overwrite").parquet(
    "hdfs:///data/auction/processed/anomaly/"
)

print("[완료] 이상치 탐지 완료")
spark.stop()
