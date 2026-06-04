# -*- coding: utf-8 -*-
"""
Spark 전처리 스크립트
- JSON 원본 → 정제 → 원가 계산 JOIN → Parquet 저장
Usage:
    spark-submit src/pipeline/preprocess.py
"""

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

# ── Spark 세션 ────────────────────────────────────────────────────────────────
spark = SparkSession.builder \
    .appName("LostArk_Auction_Preprocess") \
    .enableHiveSupport() \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

HDFS_RAW       = "hdfs:///user/maria_dev/auction/raw/*/*/*.json"
HDFS_PROCESSED = "hdfs:///user/maria_dev/auction/processed/"
HDFS_RECIPE    = "hdfs:///user/maria_dev/auction/recipe/oreha_recipe.csv"

# ── 1. 원본 JSON 읽기 ─────────────────────────────────────────────────────────
print("[1/4] 원본 데이터 로딩...")
df_raw = spark.read.option("multiLine", "true").json(HDFS_RAW)

# ── 2. 정제 ──────────────────────────────────────────────────────────────────
print("[2/4] 데이터 정제...")
df_clean = df_raw \
    .dropna(subset=["item_name", "price"]) \
    .filter(F.col("price") > 0) \
    .withColumn("collected_at", F.to_timestamp("collected_at")) \
    .withColumn("price", F.col("price").cast("long")) \
    .withColumn("day_of_week", F.dayofweek("collected_at")) \
    .withColumn("hour_of_day", F.hour("collected_at"))

# ── 3. 레시피 JOIN → 원가 계산 ───────────────────────────────────────────────
print("[3/4] 원가 계산 JOIN...")
df_recipe = spark.read \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .csv(HDFS_RECIPE)

# 재료별 가격 추출 (생활재료만)
df_material = df_clean.filter(F.col("category").isin(
    ["식물채집", "벌목", "채광", "수렵", "낚시", "고고학"])) \
    .select("collected_at", "item_name", "price") \
    .withColumnRenamed("item_name", "material_name") \
    .withColumnRenamed("price", "material_price")

# 레시피 JOIN → 재료별 비용 계산
df_cost = df_recipe.join(df_material, on="material_name", how="inner") \
    .withColumn("material_cost", F.col("material_price") * F.col("quantity"))

# 오레하 제작 원가 합산 (재료비 합계 + 수수료)
df_craft_cost = df_cost.groupBy("result_item", "collected_at", "craft_fee") \
    .agg(
        F.sum("material_cost").alias("total_material_cost")
    ) \
    .withColumn("craft_cost", F.col("total_material_cost") + F.col("craft_fee"))

# 오레하 경매장가 추출
df_oreha = df_clean.filter(
    (F.col("category") == "재련재료") &
    (F.col("item_name").isin([
        "오레하 융화 재료", "상급 오레하 융화 재료", "최상급 오레하 융화 재료",
        "아비도스 융화 재료", "상급 아비도스 융화 재료"
    ]))) \
    .select("collected_at", "item_name", "price", "day_of_week") \
    .withColumnRenamed("item_name", "result_item") \
    .withColumnRenamed("price", "market_price")

# 원가 vs 경매장가 비교 → profit 컬럼 생성
df_profit = df_oreha.join(df_craft_cost, on=["result_item", "collected_at"], how="inner") \
    .withColumn("profit", F.col("market_price") - F.col("craft_cost")) \
    .withColumn("is_profitable", F.col("profit") > 0)

# ── 4. Parquet 저장 ───────────────────────────────────────────────────────────
print("[4/4] Parquet 저장...")
df_clean.write.mode("overwrite").parquet(HDFS_PROCESSED + "auction_log/")
df_profit.write.mode("overwrite").parquet(HDFS_PROCESSED + "craft_profit/")

print("[완료] 전처리 완료")
print("  auction_log: {}건".format(df_clean.count()))
print("  craft_profit: {}건".format(df_profit.count()))

spark.stop()
