select * from df_orders

/* Now if we look in our table columns where we can see varchar(max) which takes the many space
so trying to change this, so we will drop the table first
Then we will create the empty table with all columns again with the same name */

DROP TABLE df_orders

create table df_orders (
[order_id] int primary key
,[order_date] date
,[ship_mode] varchar(20)
,[segment] varchar(20)
,[country] varchar(20)
,[city] varchar(20)
,[state] varchar(20)
,[postal_code] varchar(20)
,[region] varchar(20)
,[category] varchar(20)
,[sub_category] varchar(20)
,[product_id] varchar(20)
,[quantity] int
,[discount] decimal(7,2)
,[sale_price] decimal(7,2)
,[profit] decimal(7,2)
)


select * from df_orders

-- find top 10 highest revenue generating products
SELECT top 10 product_id, sum(sale_price) as sales 
FROM df_orders
GROUP BY product_id
ORDER BY sales DESC

-- find top 5 higest saling products in each region
with cte as (
SELECT region, product_id, sum(sale_price) as sales 
FROM df_orders
GROUP BY region, product_id
)
select * from(
select *, ROW_NUMBER() OVER(PARTITION by region order by sales desc) as index_column
from cte) A
WHERE index_column<=5

-- find month over month growth comparision for 2022 and 2023 sales eg : jan 2022 vs jan 2023
with cte as (
select YEAR(order_date) as order_year, MONTH(order_date) as order_month, 
sum(sale_price) as sales 
from df_orders
group by YEAR(order_date), MONTH(order_date)
-- order by YEAR(order_date), MONTH(order_date)   /*Order by is not allowed inside the subquery*/
)
select order_month,
SUM(case when order_year=2022 then sales 
else 0 end) as sales_2022,
SUM(case when order_year=2023 then sales 
else 0 end) as sales_2023
from cte
group by order_month
order by order_month


-- for each category which month had highest grwoth by profit in 2023 compare to 2022

with cte as (
select category, FORMAT(order_date, 'yyyyMM') as order_year_month, 
SUM(sale_price) as sales 
from df_orders
GROUP BY category, FORMAT(order_date, 'yyyyMM')
-- ORDER BY category, FORMAT(order_date, 'yyyyMM')
)
select * from (select *, 
ROW_NUMBER() OVER(partition by category order by sales desc) as rn 
from cte) a
where rn=1

-- which sub category had highest grwoth by profit in 2023 compare to 2022
with cte as (
select sub_category, YEAR(order_date) as order_year, 
sum(sale_price) as sales 
from df_orders
group by sub_category, YEAR(order_date)
-- order by YEAR(order_date), MONTH(order_date)   /*Order by is not allowed inside the subquery*/
),
cte2 as (
select sub_category,
SUM(case when order_year=2022 then sales 
else 0 end) as sales_2022,
SUM(case when order_year=2023 then sales 
else 0 end) as sales_2023
from cte
group by sub_category
)
select *, 
(sales_2023 - sales_2022) * 100 / (sales_2022) as highest_percentage_growth
from cte2
order by highest_percentage_growth desc
-- order by sub_category


