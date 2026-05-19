"""
Q3: 생활 재료 간 가격 동조화 분석
"빙하의 숨결, 수렵물 등 재료 가격이 같이 움직이는가?"
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

HDFS_PROCESSED = "hdfs:///data/auction/processed/auction_log/"
TARGET_ITEMS = ["빙하의 숨결", "수렵물", "채집물", "벌목물", "광물"]

# 생활재료만 필터링
df = spark.read.parquet(HDFS_PROCESSED) \
    .filter(F.col("category") == "생활재료") \
    .filter(F.col("item_name").isin(TARGET_ITEMS)) \
    .select("collected_at", "item_name", "price")

# 시간대별 아이템별 평균가 피벗
df_pivot = df.groupBy("collected_at") \
    .pivot("item_name", TARGET_ITEMS) \
    .agg(F.avg("price"))

df_pivot.cache()

# 아이템 쌍별 상관계수 계산
print("\n[Q3] 생활재료 간 가격 상관계수")
print("-" * 50)
for i, item_a in enumerate(TARGET_ITEMS):
    for item_b in TARGET_ITEMS[i+1:]:
        try:
            corr = df_pivot.stat.corr(item_a, item_b)
            print(f"  {item_a} ↔ {item_b}: {corr:.4f}")
        except Exception as e:
            print(f"  {item_a} ↔ {item_b}: 계산 불가 ({e})")

# 결과 저장
df_pivot.write.mode("overwrite").parquet(
    "hdfs:///data/auction/processed/material_pivot/"
)

print("\n[완료] 상관분석 완료")
spark.stop()
