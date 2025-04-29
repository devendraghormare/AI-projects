FEW_SHOT_SQL_EXAMPLES = """
Example 1:
Question: Find products where average rating improved over time (e.g., monthly average rating is increasing).

❌ Incorrect SQL (fails due to use of window function in HAVING clause):
SELECT 
    products.product_id, 
    products.name, 
    AVG(reviews.rating) AS average_rating, 
    DATE_TRUNC('month', reviews.created_at) AS month
FROM 
    products
JOIN 
    reviews ON products.product_id = reviews.product_id
GROUP BY 
    products.product_id, 
    products.name, 
    DATE_TRUNC('month', reviews.created_at)
HAVING 
    AVG(reviews.rating) > LAG(AVG(reviews.rating)) OVER (PARTITION BY products.product_id ORDER BY DATE_TRUNC('month', reviews.created_at))
ORDER BY 
    products.product_id, 
    DATE_TRUNC('month', reviews.created_at);

❗ Problem: Window functions like `LAG()` are not allowed in the HAVING clause in PostgreSQL.

✅ Correct SQL:
WITH monthly_aggregates AS (
    SELECT product_id, DATE_TRUNC('month', created_at) AS month, AVG(rating) AS avg_rating
    FROM reviews
    GROUP BY product_id, month
),
with_lag AS (
    SELECT *,
           LAG(avg_rating) OVER (PARTITION BY product_id ORDER BY month) AS prev_avg_rating
    FROM monthly_aggregates
)
SELECT *
FROM with_lag
WHERE avg_rating > prev_avg_rating;
"""
