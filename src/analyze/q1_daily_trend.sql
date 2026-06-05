-- Q1: 요일/시간대별 아이템 시세 패턴 분석
-- "레이드 초기화(수요일) 전후로 시세가 어떻게 변하는가?"
-- Usage: hive -f src/analyze/q1_daily_trend.sql
USE auction;

-- 요일별 평균/최저/최고가
SELECT
    category,
    item_name,
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
    ROUND(AVG(price), 0)  AS avg_price,
    MIN(price)            AS min_price,
    MAX(price)            AS max_price,
    COUNT(*)              AS record_count
FROM auction_log
WHERE category IN ('유물각인서', '재련재료', '재련추가')
GROUP BY category, item_name, day_of_week
ORDER BY category, item_name, day_of_week;
