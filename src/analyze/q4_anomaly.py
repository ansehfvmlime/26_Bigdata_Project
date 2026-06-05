# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
import codecs
import os
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = SparkSession.builder \
    .appName("LostArk_Q4_Anomaly") \
    .enableHiveSupport() \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

HDFS_PROCESSED = "hdfs:///user/maria_dev/auction/processed/auction_log/"
OUTPUT_DIR = "results"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "q4_result.txt")

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

df = spark.read.parquet(HDFS_PROCESSED) \
    .filter(F.col("category") == "유물각인서")

df_stats = df.groupBy("item_name") \
    .agg(
        F.avg("price").alias("avg_price"),
        F.stddev("price").alias("std_price"),
        F.count("*").alias("total_count")
    )

df_with_stats = df.join(df_stats, on="item_name", how="inner") \
    .withColumn("lower_bound", F.col("avg_price") - 2 * F.col("std_price")) \
    .withColumn("is_anomaly", F.col("price") < F.col("lower_bound")) \
    .withColumn("discount_pct",
        F.round((1 - F.col("price") / F.col("avg_price")) * 100, 1))

df_anomaly = df_with_stats.filter(F.col("is_anomaly") == True)

lines = []
lines.append("[Q4] 유물각인서 이상치 탐지 결과 (덤핑 의심 매물)")
lines.append("-" * 60)
lines.append("  전체 레코드: {}건".format(df.count()))
lines.append("  이상치 탐지: {}건".format(df_anomaly.count()))
lines.append("")
lines.append("[아이템별 이상치 발생 빈도 Top 20]")
lines.append("-" * 60)

rows = df_anomaly.groupBy("item_name") \
    .agg(
        F.count("*").alias("anomaly_count"),
        F.round(F.avg("discount_pct"), 1).alias("avg_discount_pct"),
        F.round(F.avg("avg_price"), 0).alias("avg_price"),
        F.min("price").alias("min_anomaly_price")
    ) \
    .orderBy(F.desc("anomaly_count")) \
    .limit(20) \
    .collect()

for row in rows:
    lines.append("  {} | 이상치 {}건 | 평균가 {}골드 | 평균할인 {}% | 최저 {}골드".format(
        row.item_name,
        row.anomaly_count,
        int(row.avg_price),
        row.avg_discount_pct,
        row.min_anomaly_price
    ))

lines.append("")
lines.append("[요일별 이상치 발생 빈도]")
lines.append("-" * 60)

day_rows = df_anomaly.groupBy("day_of_week") \
    .agg(F.count("*").alias("anomaly_count")) \
    .orderBy("day_of_week") \
    .collect()

day_map = {1:"일", 2:"월", 3:"화", 4:"수", 5:"목", 6:"금", 7:"토"}
for row in day_rows:
    lines.append("  {}요일({}): {}건".format(
        day_map.get(row.day_of_week, "?"),
        row.day_of_week,
        row.anomaly_count
    ))

lines.append("")
lines.append("[완료] Q4 이상치 탐지 완료")

with codecs.open(OUTPUT_FILE, "w", "utf-8") as f:
    for line in lines:
        f.write(line + "\n")

df_anomaly.write.mode("overwrite").parquet(
    "hdfs:///user/maria_dev/auction/processed/anomaly/"
)

spark.stop()
