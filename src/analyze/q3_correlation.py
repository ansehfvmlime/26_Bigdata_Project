# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
import codecs
import os
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = SparkSession.builder \
    .appName("LostArk_Q3_Correlation") \
    .enableHiveSupport() \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

HDFS_PROCESSED = "hdfs:///user/maria_dev/auction/processed/auction_log/"
TARGET_CATEGORIES = ["재련재료", "재련추가"]
OUTPUT_DIR = "results"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "q3_result.txt")

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

df = spark.read.parquet(HDFS_PROCESSED) \
    .filter(F.col("category").isin(TARGET_CATEGORIES)) \
    .select("category", "item_name", "day_of_week", "price")

df.cache()

lines = []
lines.append("[Q3] 요일과 가격 간 상관계수 분석")
lines.append("=" * 60)
lines.append("[1] 카테고리별 요일-가격 상관계수")
lines.append("-" * 40)

for cat in TARGET_CATEGORIES:
    df_cat = df.filter(F.col("category") == cat)
    corr = df_cat.stat.corr("day_of_week", "price")
    direction = "양(+)" if corr > 0 else "음(-)"
    strength = "강" if abs(corr) > 0.3 else ("중" if abs(corr) > 0.1 else "약")
    lines.append("  {}: {:.4f} ({} {})".format(cat, corr, direction, strength))

lines.append("[2] 아이템별 요일-가격 상관계수")
lines.append("-" * 40)

items = [row.item_name for row in df.select("item_name").distinct().collect()]

results = []
for item in items:
    df_item = df.filter(F.col("item_name") == item)
    count = df_item.count()
    if count < 50:
        continue
    corr = df_item.stat.corr("day_of_week", "price")
    results.append((item, corr, count))

results.sort(key=lambda x: abs(x[1]), reverse=True)

lines.append("  상관관계 강한 상위 10개:")
for item, corr, count in results[:10]:
    direction = "양(+)" if corr > 0 else "음(-)"
    lines.append("  {}: {:.4f} ({}) [{}건]".format(item, corr, direction, count))

lines.append("  상관관계 약한 하위 10개:")
for item, corr, count in results[-10:]:
    direction = "양(+)" if corr > 0 else "음(-)"
    lines.append("  {}: {:.4f} ({}) [{}건]".format(item, corr, direction, count))

lines.append("[3] 요일별 카테고리 평균가")
lines.append("-" * 40)

rows = df.groupBy("category", "day_of_week") \
    .agg(F.round(F.avg("price"), 1).alias("avg_price")) \
    .orderBy("category", "day_of_week") \
    .collect()

for row in rows:
    lines.append("  {} | 요일{} | {}골드".format(
        row.category, row.day_of_week, row.avg_price))

lines.append("[완료] Q3 상관분석 완료")

with codecs.open(OUTPUT_FILE, "w", "utf-8") as f:
    for line in lines:
        f.write(line + "\n")

spark.stop()
