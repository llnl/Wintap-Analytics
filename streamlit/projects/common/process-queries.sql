-- Dataset Summaries for Metrics

-- Hosts over time
select
--# name: data_summary
	bd.bucket_day,
	count(distinct pu.hostname) hosts,
	count(distinct process_name) uniq_processes,
	count(*) total_processes,
	count(distinct user_name) users,
	sum(mitre_num_rows) mitre,
	sum(lolbas_num_rows) lolbas,
	sum(total_sigma_hits) sigma,
	sum(label_num_hits) labels,
	sum(reg_totals) registry,
	sum(reg_reads) registry_reads,
	sum(file_num_raw_rows) file_activity,
	sum(read_events) file_reads,
	sum(net_total_events) network,
	count(dll_num_uniq_files) dlls
from
	process_uber_summary pu
join bucket_days bd on
	bd.bucket_day between cast(pu.first_seen as date) and cast(pu.last_seen as date)
group by
	ALL
order by
	all
;


select
--# name: host_count
count(*) num_hosts from ds.host
;

-- Get raw data collection range, which means we need to ignore process data reconstructed from Windows logs, which are activitytype="refresh"
select
--# name: raw_data_range
	to_timestamp(ds.win32_to_epoch(min(eventtime))) first_seen,
	to_timestamp(ds.win32_to_epoch(max(eventtime))) last_seen,
from
	ds.raw_process
where
	lower(activitytype)= 'start'
;


-- Get raw data collection range, which means we need to ignore process data reconstructed from Windows logs, which are activitytype="refresh"
select
--# name: data_range
	min(process_term) first_seen,
	max(process_term) last_seen,
from
	ds.process
;

-- Process centric metrics and analytics

-- Summarize processes by start/term
select 
--# name: process_life_summary
	process_life_cd,
	count(distinct process_name) uniq_process_name, 
	count(*) num_processes, 
    -- use window function to calculate the pct of grand total.
	(num_processes / sum(num_processes) over (partition by grouping(process_life_cd)))*100 pct,
from
	process_life_v1
group by rollup (process_life_cd)
order by all
;


-- Summarize processes by hostname, start/term
select 
--# name: process_life_host_summary
	hostname,
	process_life_cd,
	count(distinct process_name) uniq_process_name, 
	count(*) num_processes, 
	num_processes / sum(num_processes) over (partition by grouping(hostname, process_life_cd), hostname) pct_of_host,
from
	process_life_v1
group by
	rollup (hostname, process_life_cd)
order by all
;

-- Get count of unique process names
select 
--# name: uniq_process_count
  count(distinct process_name) uniq_count, count(*) total_processes
from process
;
