# -*- coding: utf-8 -*-
"""
Q3: 요일과 재련재료/재련추가/오레하 가격 간 상관관계 분석
"요일이 가격에 유의미한 영향을 주는가?"
Usage:
    spark-submit src/analyze/q3_correlation.py
"""
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = SparkSession.builder \
    .appName("LostArk_Q3_Correlation") \
    .enableHiveSupport() \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

HDFS_PROCESSED = "hdfs:///user/maria_dev/auction/processed/auction_log/"

TARGET_CATEGORIES = ["재련재료", "재련추가"]

# 대상 카테고리 데이터 로드
df = spark.read.parquet(HDFS_PROCESSED) \
    .filter(F.col("category").isin(TARGET_CATEGORIES)) \
    .select("category", "item_name", "day_of_week", "price")

df.cache()

print("\n[Q3] 요일과 가격 간 상관계수 분석")
print("=" * 60)

# 1. 카테고리별 상관계수
print("\n[1] 카테고리별 요일-가격 상관계수")
print("-" * 40)
for cat in TARGET_CATEGORIES:
    df_cat = df.filter(F.col("category") == cat)
    corr = df_cat.stat.corr("day_of_week", "price")
    direction = "양(+)" if corr > 0 else "음(-)"
    strength = "강" if abs(corr) > 0.3 else ("중" if abs(corr) > 0.1 else "약")
    print("  {}: {:.4f} ({} {})".format(cat, corr, direction, strength))

# 2. 아이템별 상관계수 (상위/하위 10개)
print("\n[2] 아이템별 요일-가격 상관계수 (상관 강한 순)")
print("-" * 40)
items = [row.item_name for row in
    df.select("item_name").distinct().collect()]

results = []
for item in items:
    df_item = df.filter(F.col("item_name") == item)
    count = df_item.count()
    if count < 50:
        continue
    corr = df_item.stat.corr("day_of_week", "price")
    results.append((item, corr, count))

results.sort(key=lambda x: abs(x[1]), reverse=True)

print("\n  상관관계 강한 상위 10개:")
for item, corr, count in results[:10]:
    direction = "양(+)" if corr > 0 else "음(-)"
    print("  {}: {:.4f} ({}) [{}건]".format(item, corr, direction, count))

print("\n  상관관계 약한 하위 10개:")
for item, corr, count in results[-10:]:
    direction = "양(+)" if corr > 0 else "음(-)"
    print("  {}: {:.4f} ({}) [{}건]".format(item, corr, direction, count))

# 3. 요일별 카테고리 평균가 (Q1 심화)
print("\n[3] 요일별 카테고리 평균가")
print("-" * 40)
df.groupBy("category", "day_of_week") \
    .agg(F.round(F.avg("price"), 1).alias("avg_price")) \
    .orderBy("category", "day_of_week") \
    .show(30, truncate=False)

print("\n[완료] Q3 상관분석 완료")
spark.stop()