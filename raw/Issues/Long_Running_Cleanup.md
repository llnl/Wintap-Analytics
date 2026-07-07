# Issues observed for long running instances

* When the time partitioned directories in raw_sensor are emptied, during a file upload, the directories should be removed
* Over time, the number of processes built up in the event_store duckdb grows significantly. A specifc example found ~8M rows over 10 days, with just 1/3 having "exit_codes".
    * Why is Lintap missing so many process terminations?
    * We need a cleanup routine on the database: the intention is that it is a store for "currentish" processes.
    * CPU load grows significantly as the DB grows. Confirm this correlation hypothesis
* Improve pidstat-collector.sh ro run alongside lintap and push data to S3. This would help understanding CPU/memory use over time and in relation to system load
