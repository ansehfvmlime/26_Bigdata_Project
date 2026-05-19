-- Q2: 영지 제작 vs 경매장 구매 이득 분석
-- "언제, 얼마나 제작이 이득인가?"
-- Usage: hive -f src/analyze/q2_craft_profit.sql

USE auction;

-- 요일별 제작 이득 평균 및 이득 비율
SELECT
    result_item,
    day_of_week,
    CASE day_of_week
        WHEN 1 THEN '일'
        WHEN 2 THEN '월'
        WHEN 3 THEN '화'
        WHEN 4 THEN '수'
        WHEN 5 THEN '목'
        WHEN 6 THEN '금'
        WHEN 7 THEN '토'
    END AS day_label,
    ROUND(AVG(profit), 0)                                         AS avg_profit,
    ROUND(AVG(craft_cost), 0)                                     AS avg_craft_cost,
    ROUND(AVG(market_price), 0)                                   AS avg_market_price,
    ROUND(SUM(CASE WHEN is_profitable THEN 1 ELSE 0 END)
          / COUNT(*) * 100, 1)                                    AS profitable_pct
FROM craft_profit
GROUP BY result_item, day_of_week
ORDER BY result_item, day_of_week;
