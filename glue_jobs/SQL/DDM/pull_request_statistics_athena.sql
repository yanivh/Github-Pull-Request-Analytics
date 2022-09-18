-- see the median pull request closure times for different dates
select
       approx_percentile(time_open_to_merge_seconds,0.5)/60 as minutes_median,
       sum (time_open_to_merge_seconds)/60 as minutes_sum,
       count(*) as pr_count,
       state,
       date
from pull_request
where state ='closed'
group by state, date


-- open ticket per days
SELECT state,
        date,
        sum ((CAST(time_cretead_to_update_seconds  AS double) / 86400)) as days_time_open
        -- ,"create_at"
FROM "git"."pull_request"
where state ='open'
group by date,state
order by days_time_open asc
;


--  add new partitions
MSCK REPAIR TABLE `pull_request_pull_request`;