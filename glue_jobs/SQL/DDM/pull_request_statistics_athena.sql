-- see the median pull request closure times for different dates
CREATE VIEW view_pr_merged_median AS

select
       approx_percentile(time_open_to_merge_seconds,0.5)/60 as minutes_median,
       sum (time_open_to_merge_seconds)/60 as minutes_sum,
       count(*) as pr_count,
       state,
       date
from pull_requests
where state ='closed'
group by state, date


-- open ticket per days
CREATE VIEW view_tickets_open AS

SELECT state,
        date,
        sum ((CAST(time_cretead_to_update_seconds  AS double) / 86400)) as days_time_open,
        count(*) as pr_count
FROM "git"."pull_requests"
where state ='open'
group by date,state
order by days_time_open asc
;


--  add new partitions
MSCK REPAIR TABLE `pull_requests`;