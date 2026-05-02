select * from df_netflix_raw
order by title

/* So now, some other language characters will come here with ???? in varchar, so we need to make it as nvarchar 
So it will so in original language and always creat a table and give the char length manually and create table
then append the values from the pyhton
*/
DROP TABLE [dbo].[df_netflix_raw]

CREATE TABLE [dbo].[df_netflix_raw](
	[show_id] [varchar](10) NULL,
	[type] [varchar](10) NULL,
	[title] [NVARCHAR](200) NULL,
	[director] [varchar](250) NULL,
	[cast] [varchar](1000) NULL,
	[country] [varchar](150) NULL,
	[date_added] [varchar](20) NULL,
	[release_year] [int] NULL,
	[rating] [varchar](10) NULL,
	[duration] [varchar](10) NULL,
	[listed_in] [varchar](100) NULL,
	[description] [varchar](500) NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO

select * from df_netflix_raw
where show_id='s5023'

-- remove the duplicates

-- let's check if there are no duplicates in show_id column then we will make it as primary key
select show_id, COUNT(*) 
from df_netflix_raw
group by show_id
having COUNT(*)>1

DROP TABLE [dbo].[df_netflix_raw]

CREATE TABLE [dbo].[df_netflix_raw](
	[show_id] [varchar](10) primary key,
	[type] [varchar](10) NULL,
	[title] [NVARCHAR](200) NULL,
	[director] [varchar](250) NULL,
	[cast] [varchar](1000) NULL,
	[country] [varchar](150) NULL,
	[date_added] [varchar](20) NULL,
	[release_year] [int] NULL,
	[rating] [varchar](10) NULL,
	[duration] [varchar](10) NULL,
	[listed_in] [varchar](100) NULL,
	[description] [varchar](500) NULL
)


select * from df_netflix_raw
where show_id='s5023'

select title, COUNT(*) 
from df_netflix_raw
group by title
having COUNT(*)>1

select * from df_netflix_raw
where title in (
select title 
from df_netflix_raw
group by title
having COUNT(*)>1
)
order by title

/* If the type is different then it is fine but everything is same in whole row then remove it*/

select * from df_netflix_raw
where concat(upper(title), type) in (  -- here we cannot use two columns, so we need to concat here
select concat(upper(title), type) 
from df_netflix_raw
group by concat(upper(title), type)
having COUNT(*)>1
)
order by title

/*The below line of code will remove the duplicates which has row number as 2, so it will just take the row number 1*/
with cte as (
select *, ROW_NUMBER() OVER(PARTITION BY title, type order by show_id) as rn
from df_netflix_raw
)
select * from cte
where rn=1


-- new table for listed in, director, country, cast

/* STRING_SPLIT is used in SQL Server to normalize denormalized comma-separated data into rows. 
It is commonly used with CROSS APPLY for analytics and filtering

Suppost table as below
| title   | listed_in      |
| ------- | -------------- |
| Movie A | Action,Drama   |
| Movie B | Comedy,Romance |

SELECT 
    title,
    value AS genre
FROM df_netflix_raw
CROSS APPLY STRING_SPLIT(listed_in, ',');

Genre - simply means a category or type used to group similar things—most commonly movies, books, music, or shows

OUTPUT will be:
Movie A | Action
Movie A | Drama
Movie B | Comedy
Movie B | Romance
*/

select show_id, trim(value) as director  -- trim(value), so trim will remove the extra spaces
into netflix_directors
from df_netflix_raw
cross apply string_split(director,',')

select * from netflix_directors

-- do for the country
select show_id, trim(value) as country  -- trim(value), so trim will remove the extra spaces
into netflix_country
from df_netflix_raw
cross apply string_split(country,',')

select * from netflix_country

-- do for the cast
select show_id, trim(value) as genre  -- trim(value), so trim will remove the extra spaces
into netflix_genre
from df_netflix_raw
cross apply string_split(listed_in,',')

select * from netflix_genre


-- data type conversions for date added
with cte as (
select *, ROW_NUMBER() OVER(PARTITION BY title, type order by show_id) as rn
from df_netflix_raw
)
select show_id, type, title, cast(date_added as date) as date_added, release_year,
rating, duration, description
from cte
where rn=1

-- populate missing values in country, duration columns

select show_id, country 
from df_netflix_raw
where country is null

select * from netflix_country where show_id='s1001'  -- in this the null values will be autometically removed because we have used the string_split command

/* not to populate the values let's check the director name and country, so we can get the idea */
select * from df_netflix_raw where director='Ahishor Solomon'
/* so now if director is same then we can populate that country which are avilable */

select director, country 
from netflix_country nc
INNER JOIN netflix_directors nd
ON nc.show_id = nd.show_id
group by director, country -- want to see the unique combination
order by director  -- maybe some director created a movie in also different different countries

/* let's take this making inside our main quesry table */

select show_id, m.country 
from df_netflix_raw nr 
INNER JOIN (
select director, country 
from netflix_country nc
INNER JOIN netflix_directors nd
ON nc.show_id = nd.show_id
group by director, country
) m
ON nr.director = m.director
where nr.country is null

/* The below code will add the missing countries name */
insert into netflix_country
select show_id, m.country 
from df_netflix_raw nr 
INNER JOIN (
select director, country 
from netflix_country nc
INNER JOIN netflix_directors nd
ON nc.show_id = nd.show_id
group by director, country
) m
ON nr.director = m.director
where nr.country is null

-- for the duration
select * 
from df_netflix_raw 
where duration is null
-- now let's check which column can help to populate the missing values

with cte as (
select *, ROW_NUMBER() OVER(PARTITION BY title, type order by show_id) as rn
from df_netflix_raw
)
select show_id, type, title, cast(date_added as date) as date_added, release_year,
rating, 
Case when duration is null then rating -- so the duration as empty cell there it will fill the data of rating of that row
else duration end as duration, description
from cte
where rn=1

/* now everything is finish, so let's make a final table*/
with cte as (
select *, ROW_NUMBER() OVER(PARTITION BY title, type order by show_id) as rn
from df_netflix_raw
)
select show_id, type, title, cast(date_added as date) as date_added, release_year,
rating, 
Case when duration is null then rating -- so the duration as empty cell there it will fill the data of rating of that row
else duration end as duration, description
into df_final_netflix
from cte
