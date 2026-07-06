-- SQL Used for Streamlit DQA

--- Find gaps larger than N
select * from (
--# name: dll_gaps_sql
SELECT 'dll' event_type,
	computername hostname,
	to_timestamp(win32_to_epoch(eventtime)) eventts,
	lag(eventtime) over (partition by computername order by eventtime) prev_eventtime,
	to_timestamp(win32_to_epoch(prev_eventtime)) prevts,
	eventtime-prev_eventtime diffms,
	eventts-to_timestamp(win32_to_epoch(prev_eventtime)) diff,
	win32_to_epoch(eventtime)-win32_to_epoch(prev_eventtime) diff_sec 
from main.raw_imageload e
/**
union all
SELECT 'net',
	to_timestamp(win32_to_epoch(FirstSeenMS)) eventts,
	lag(FirstSeenMS) over (order by FirstSeenMS) prev_eventtime,
	to_timestamp(win32_to_epoch(prev_eventtime)) prevts,
	FirstSeenMS-prev_eventtime diffms,
	eventts-to_timestamp(win32_to_epoch(prev_eventtime)) diff,
	win32_to_epoch(FirstSeenMS)-win32_to_epoch(prev_eventtime) diff_sec 
from main.raw_process_conn_incr e
**/
)
where diff > interval 10 seconds
order by hostname, eventts
;


select hostname, process_name, process_started, dll_num_uniq_files
--# name: canaries
from process_summary
where process_name in ('reg.exe','timeout.exe')
-- Skip the spurious few at the start
and cast(process_started as timestamp) > make_timestamp(2024,03,07,00,00,00)
order by process_started
;