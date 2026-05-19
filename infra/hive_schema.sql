-- Hive 테이블 DDL
-- Usage: hive -f infra/hive_schema.sql

CREATE DATABASE IF NOT EXISTS auction;
USE auction;

-- 경매장 시세 테이블 (Spark 전처리 후 Parquet 적재)
CREATE EXTERNAL TABLE IF NOT EXISTS auction_log (
    collected_at  TIMESTAMP,
    category      STRING,
    item_name     STRING,
    grade         STRING,
    price         BIGINT,
    quantity      INT,
    end_date      STRING,
    day_of_week   INT,
    hour_of_day   INT
)
STORED AS PARQUET
LOCATION 'hdfs:///data/auction/processed/auction_log/';

-- 제작 이득 테이블 (Spark preprocess.py 결과)
CREATE EXTERNAL TABLE IF NOT EXISTS craft_profit (
    result_item   STRING,
    collected_at  TIMESTAMP,
    market_price  BIGINT,
    craft_cost    BIGINT,
    profit        BIGINT,
    is_profitable BOOLEAN,
    day_of_week   INT
)
STORED AS PARQUET
LOCATION 'hdfs:///data/auction/processed/craft_profit/';

-- 레시피 테이블 (CSV)
CREATE EXTERNAL TABLE IF NOT EXISTS oreha_recipe (
    result_item   STRING,
    material_name STRING,
    quantity      INT,
    craft_fee     INT
)
ROW FORMAT DELIMITED
    FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION 'hdfs:///data/auction/recipe/'
TBLPROPERTIES ('skip.header.line.count'='1');
