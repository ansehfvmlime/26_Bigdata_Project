# -*- coding: utf-8 -*-
"""
Q3: 생활 재료 간 가격 동조화 분석
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

TARGET_ITEMS = [
    "들꽃", "목재", "철광석", "두툼한 생고기", "생선",
    "고대 유물", "아비도스 들꽃", "아비도스 목재", "아비도스 철광석"
]

CATEGORIES = ["식물채집", "벌목", "채광", "수렵", "낚시", "고고학"]

df = spark.read.parquet(HDFS_PROCESSED) \
    .filter(F.col("category").isin(CATEGORIES)) \
    .filter(F.col("item_name").isin(TARGET_ITEMS)) \
    .select("collected_at", "item_name", "price")

df_pivot = df.groupBy("collected_at") \
    .pivot("item_name", TARGET_ITEMS) \
    .agg(F.avg("price"))

df_pivot.cache()

print("\n[Q3] 생활재료 간 가격 상관계수")
print("-" * 50)
for i, item_a in enumerate(TARGET_ITEMS):
    for item_b in TARGET_ITEMS[i+1:]:
        try:
            corr = df_pivot.stat.corr(item_a, item_b)
            print("  {} <-> {}: {:.4f}".format(item_a, item_b, corr))
        except Exception as e:
            print("  {} <-> {}: 계산 불가 ({})".format(item_a, item_b, e))

df_pivot.write.mode("overwrite").parquet(
    "hdfs:///user/maria_dev/auction/processed/material_pivot/"
)
print("\n[완료] 상관분석 완료")
spark.stop()