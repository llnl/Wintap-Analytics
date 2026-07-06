-- Assume a stdview dataset is available as "DS"

-- Process Life Cycle Code
-- Base view for analytics
create view process_life_v1
as select hostname,
  agent_id,
  pid_hash,
  process_name,
  process_started,
  process_term,
  process_term-process_started duration,
  exit_code,
  case 
	    when process_started < process_term then 'Complete' 
  	  when process_started is not null and process_term is null then 'Started'
  	  when process_started is null and process_term is not null then 'No start'
  	  when process_started is null and process_term is null then 'Null'
  	  when process_started = process_term then 'Same'
  	  when process_started > process_term then 'Time Travel'
  	  else '?'
  end process_life_cd,
from process
order by duration 
;

-- Creates a table of days that represent the data range. Suitable for joining to create histogram buckets by day over time.
-- ToDo: Create an additional view for hours that is useable for short duration datasets.
create or replace view bucket_days
as
select cast((select min(first_seen) from process_uber_summary) as date)+daynum bucket_day
from (
select cast(unnest(range(0,(select date_part('day',max(last_seen)-min(first_seen))+1 from process_uber_summary))) as tinyint) daynum
)
;

