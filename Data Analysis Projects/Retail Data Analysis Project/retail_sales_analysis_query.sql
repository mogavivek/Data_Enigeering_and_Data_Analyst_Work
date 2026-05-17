CREATE DATABASE Retail_Sales_Analysis_db

USE Retail_Sales_Analysis_db
Go
DROP TABLE retail_sales;

CREATE TABLE retail_sales (
    transactions_id VARCHAR(50),
    sale_date VARCHAR(50),
    sale_time VARCHAR(50),
    customer_id VARCHAR(50),
    gender VARCHAR(50),
    age VARCHAR(50),
    category VARCHAR(50),
    quantity VARCHAR(50),
    price_per_unit VARCHAR(50),
    cogs VARCHAR(50),
    total_sale VARCHAR(50)
)
ALTER TABLE retail_sales
ALTER COLUMN transactions_id VARCHAR(50);

select * from retail_sales_analysis
where transactions_id is NULL

select * from retail_sales_analysis
where sale_date is NULL

select * from retail_sales_analysis
where sale_time is NULL

select * from retail_sales_analysis
where transactions_id is NULL OR
	  sale_date is NULL OR
	  sale_time is NULL OR
	  customer_id is NULL OR
	  gender is NULL OR
	  age is NULL OR
	  category is NULL OR
	  quantiy is NULL OR
	  price_per_unit is NULL OR
	  cogs is NULL OR
	  total_sale is NULL

delete from retail_sales_analysis
where transactions_id is NULL OR
	  sale_date is NULL OR
	  sale_time is NULL OR
	  customer_id is NULL OR
	  gender is NULL OR
	  age is NULL OR
	  category is NULL OR
	  quantiy is NULL OR
	  price_per_unit is NULL OR
	  cogs is NULL OR
	  total_sale is NULL

-- Data Analysis & Business Key Problems & Answers

select COUNT(*) as total_sale from retail_sales_analysis

-- How many customers we have
select COUNT(DISTINCT customer_id) as total_customer from retail_sales_analysis

-- How many category we have
select DISTINCT category from retail_sales_analysis

-- My Analysis & Findings
-- Q.1 Write a SQL query to retrieve all columns for sales made on '2022-11-05'

select * 
from retail_sales_analysis
where sale_date = '2022-11-05'

-- Q.2 Write a SQL query to retrieve all transactions where the category is 'Clothing' and the quantity sold is more than 4 in the month of Nov-2022
select *
from retail_sales_analysis
where category = 'Clothing'
	AND
	FORMAT(sale_date, 'yyyy-MM') = '2022-11'
	AND
	quantiy >= 4

-- Q.3 Write a SQL query to calculate the total sales (total_sale) for each category.

select category, 
SUM(total_sale) as net_sale,
COUNT(*) as total_orders
from retail_sales_analysis
group by category


-- Q.4 Write a SQL query to find the average age of customers who purchased items from the 'Beauty' category.

select ROUND(AVG(age), 2) as avg_age
from retail_sales_analysis
where category = 'Beauty'

-- Q.5 Write a SQL query to find all transactions where the total_sale is greater than 1000.

select * from retail_sales_analysis
where total_sale > 1000

-- Q.6 Write a SQL query to find the total number of transactions (transaction_id) made by each gender in each category.

select category, gender, COUNT(*) as total_transaction 
from retail_sales_analysis
group by category, gender

-- Q.7 Write a SQL query to calculate the average sale for each month. Find out best selling month in each year

select  
	year_num,
	month_num,
	avg_sale
from
(
	select
		YEAR(sale_date) AS year_num, 
		MONTH(sale_date) AS month_num,
		AVG(total_sale) as avg_sale,
		RANK() OVER(PARTITION BY YEAR(sale_date) ORDER BY AVG(total_sale) DESC) as ranking
	from retail_sales_analysis
	group by YEAR(sale_date), MONTH(sale_date)
	-- order by YEAR(sale_date), AVG(total_sale) DESC    (this is not required because we writing in RANK())
) as t1
where ranking = 1


-- Q.8 Write a SQL query to find the top 5 customers based on the highest total sales 

select top 5 customer_id, SUM(total_sale) as total_customer_purchase
from retail_sales_analysis
group by customer_id
order by SUM(total_sale) DESC

-- Q.9 Write a SQL query to find the number of unique customers who purchased items from each category.

select 
	category, 
	COUNT(DISTINCT customer_id) as count_of_unique_customer
from retail_sales_analysis
group by category

-- Q.10 Write a SQL query to create each shift and number of orders (Example Morning <=12, Afternoon Between 12 & 17, Evening >17)

select * from retail_sales_analysis

with hourly_sale 
as
(
	/* Now we cannot write the group by here, it will make a complecated so creating the cte of this query */
	select *, 
		CASE
			WHEN DATEPART(HOUR, sale_time) <= 12 THEN 'Morning'
			WHEN DATEPART(HOUR, sale_time) BETWEEN 12 AND 17 THEN 'Afternoon'
			ELSE 'Evening' END as shift_time
	from retail_sales_analysis
)
select 
	shift_time,
	COUNT(*) as total_orders
from hourly_sale
group by shift_time