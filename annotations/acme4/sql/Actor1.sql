/**
  
Actor 1 Activity

Identifiers:

Linux Host: Katoolin (172.31.36.31)
Windows User:

Unique commands: lsasss.exe, explorerr.exe, certutil.exe

Times of activity:
  
 **/

-- Network connections beteen linux and windows
-- Note: we don't generally have the Linux side, so filter by remote_ip_addr. 
select local_ip_addr, remote_ip_addr, process_name, min(first_seen), max(last_seen), count(distinct remote_port), count(*), any_value(pid_hash)
from main.process_net_conn
where remote_ip_addr='172.31.36.31'
group by ALL order by all
;

-- All user activity
SELECT hostname, user_name, min(first_seen), max(last_seen), count(distinct process_name), count(*)
from process
where user_name like 'ACME%'
group by ALL 
order by all
;

-- Bad user activity
SELECT hostname, user_name, min(first_seen), max(last_seen), count(distinct process_name), count(*)
from process
where user_name like 'ACME\bad%'
group by ALL 
order by all
;

-- Benignware Processes
SELECT hostname, process_name, min(first_seen), max(last_seen), count(distinct user_name), count(*)
from process
where process_name like 'splunk%' or process_name like 'putty%'
group by ALL 
order by all
;

-- Event logs? Yes!
select filename, count(distinct hostname), count(*) from main.process_file 
where filename like '%evtx'
group by all
order by count(*) desc
;





