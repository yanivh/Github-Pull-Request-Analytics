-- see the median pull request closure times for different dates
select
       approx_percentile(open_to_merge_seconds,0.5)/60 as median_minutes,
       sum (open_to_merge_seconds)/60 as minutes,
       count(*) as _count,
       state,
       date
from pull_request_pull_request
where state ='closed'
group by state, date


-- open ticket per days
SELECT state,
        date,
        (CAST(open_to_merge_seconds AS double) / 86400) days_open_merge,
        (CAST("time_open__seconds"  AS double) / 86400) days_time_open,
        "closed_at",
        "create_at",
        "merged_at"
FROM "git"."pull_request_pull_request"
where state ='open'
order by days_open_merge asc ;

--  add new partitions
MSCK REPAIR TABLE `pull_request_pull_request`;