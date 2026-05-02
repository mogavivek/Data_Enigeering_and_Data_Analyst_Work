USE master;
Go

SELECT TABLE_CATALOG, TABLE_SCHEMA, TABLE_NAME
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_NAME = 'df_final_netflix';
/*1.  for each director count the no of movies and tv shows created by them in separate columns 
for directors who have created tv shows and movies both */

select nd.director , 
COUNT(distinct case when fn.type='Movie' then fn.show_id end) as no_of_movies,
COUNT(distinct case when fn.type='TV Show' then fn.show_id end) as no_of_tv_shows,
COUNT(distinct fn.type) as distinct_type
from dbo.df_final_netflix as fn
INNER JOIN netflix_directors as nd
ON fn.show_id = nd.show_id
group by nd.director
having count(distinct fn.type) >1
order by distinct_type desc


/* 2. which country has highest number of comedy movies*/

select ng.show_id, nc.country
from netflix_genre as ng
INNER JOIN netflix_country as nc
ON ng.show_id = nc.show_id
where ng.genre = 'Comedies'

-- now in above we alreadz filtered the comedies movie with regards the country not we have to count the country

select top 1 nc.country, COUNT(distinct ng.show_id) as no_of_movies -- top 1 will give the first movie name
from netflix_genre as ng
INNER JOIN netflix_country as nc
ON ng.show_id = nc.show_id
INNER JOIN df_final_netflix as fn  -- second table we are joining because type is in this table
ON ng.show_id = fn.show_id
where ng.genre = 'Comedies' and fn.type='Movie'
group by nc.country
order by no_of_movies DESC

/* 3. for each year (as per date added to netflix), which director has maximum number of movies released */
with cte as (
select nd.director, YEAR(fn.date_added) as date_year, COUNT(distinct fn.show_id) as no_of_movies -- we write the distinct to avoid the duplicate while joining the table
from df_final_netflix as fn
INNER JOIN netflix_directors as nd
ON fn.show_id = nd.show_id
where fn.type='Movie'
group by nd.director, YEAR(fn.date_added)
)
, cte2 as (
select *, ROW_NUMBER() OVER(PARTITION BY date_year order by no_of_movies desc, director) as rn  -- partition by date because we have to check in each year that is why
from cte
-- order by date_year, no_of_movies desc
)
select * from cte2
where rn=1


/* 4. what is average duration of movies in each genre */


select ng.genre, avg(CAST(REPLACE(duration, ' min', '') as int)) as average_duration
from df_final_netflix as fn
INNER JOIN netflix_genre as ng
ON fn.show_id = ng.show_id
where fn.type='Movie'
group by ng.genre

/* 5. find the list of directors who have created Documentaries and comedy movies both.
display director names along with number of comedy and horror movies directed by them*/


select nd.director, 
COUNT(distinct case when ng.genre = 'Comedies' then fn.show_id end) as no_of_comedy,
COUNT(distinct case when ng.genre = 'Documentaries' then fn.show_id end) as no_of_documentaries
from df_final_netflix as fn
INNER JOIN netflix_genre as ng
ON fn.show_id = ng.show_id
INNER JOIN netflix_directors as nd
ON fn.show_id = nd.show_id
where fn.type='Movie' and ng.genre in ('Comedies', 'Documentaries')
group by nd.director
having COUNT(distinct ng.genre) = 2 -- writing 2 because we need the directors name who created both this genre

-- let's cross verify the above answer
select * from netflix_genre
where show_id in (
select show_id from netflix_directors
where director = 'Steve Brill')
order by genre