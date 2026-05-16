USE walmart_db
Go

select * from df_walmart

select COUNT(*) from df_walmart

select payment_method, COUNT(*)
from df_walmart
group by payment_method

-- Business Problem Q1: Find different payment methods, number of transactions, and quantity sold by payment method
select payment_method, 
COUNT(*) as no_payments,
SUM(quantity) as no_qty_sold
from df_walmart
group by payment_method


-- Project Question #2: Identify the highest-rated category in each branch
-- Display the branch, category, and avg rating

select * from
(select branch, 
category, 
AVG(rating) as avg_rating,
RANK() OVER(PARTITION BY branch order by AVG(rating) DESC) as ranking
from df_walmart
group by branch, category
) as t
where ranking = 1

-- Q3: Identify the busiest day for each branch based on the number of transactions

select * from
(select 
branch, 
DATENAME(WEEKDAY, TRY_CONVERT(DATE, date, 5)) as day_name,
COUNT(*) as no_tran,
RANK() OVER(PARTITION BY branch order by COUNT(*) DESC) as ranking
from df_walmart
group by branch, DATENAME(WEEKDAY, TRY_CONVERT(DATE, date, 5))
) as new_table
where ranking = 1


-- Q4: Calculate the total quantity of items sold per payment method

select payment_method, COUNT(quantity) as total_quantity 
from df_walmart
group by payment_method

-- Q5: Determine the average, minimum, and maximum rating of categories for each city

select city, category, 
MIN(rating) as min_rating,
MAX(rating) as max_rating,
AVG(rating) as avg_rating
from df_walmart
group by city, category


-- Q6: Calculate the total profit for each category

select category,
SUM(total) as revenue, 
SUM(total * profit_margin) as profit
from df_walmart
group by category

-- Q7: Determine the most common payment method for each branch, display branch and the preferred_payment_method
with cte as
(select branch, payment_method,
COUNT(*) as total_tran,
RANK() OVER(PARTITION BY branch order by COUNT(*) DESC) as ranking
from df_walmart
group by branch, payment_method)
select *
from cte
where ranking = 1

-- Q8: Categorize sales into 3 groups Morning, Afternoon, and Evening shifts
-- Find out each of the shift and number of invoices

SELECT branch,
	CASE
		WHEN DATEPART(HOUR, CAST(time AS TIME)) < 12 THEN 'Morning'
		WHEN DATEPART(HOUR, CAST(time AS TIME)) BETWEEN 12 AND 17 THEN 'Afternoon'
		ELSE 'Evening' END AS shift_time,
		COUNT(*)
FROM df_walmart
group by branch, CASE
		WHEN DATEPART(HOUR, CAST(time AS TIME)) < 12 THEN 'Morning'
		WHEN DATEPART(HOUR, CAST(time AS TIME)) BETWEEN 12 AND 17 THEN 'Afternoon'
		ELSE 'Evening' END
order by branch, COUNT(*) DESC

-- Q9: Identify the 5 branches with the highest revenue decrease ratio from last year to current year 
-- (e.g., last year 2022 to current year 2023)

-- revenue decrease ratio = (last_year_revenue - current_year_revenue / last_year_revenue) * 100

-- 2022 sales
with revenue_2022 as (
select branch, 
SUM(total) as revenue
from df_walmart
where YEAR(CONVERT(DATE, date, 5)) = 2022
group by branch
),
revenue_2023 as
(
select branch, 
SUM(total) as revenue
from df_walmart
where YEAR(CONVERT(DATE, date, 5)) = 2023
group by branch
)
select top 5 last_year_sale.branch,
last_year_sale.revenue as last_year_revenue,
current_year_sale.revenue as current_year_revenue,
ROUND(((last_year_sale.revenue - current_year_sale.revenue) / last_year_sale.revenue) * 100, 2) as revenue_decrease_ratio
from revenue_2022 as last_year_sale
JOIN revenue_2023 as current_year_sale
ON last_year_sale.branch = current_year_sale.branch
WHERE last_year_sale.revenue > current_year_sale.revenue
order by 4 DESC