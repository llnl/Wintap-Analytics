# Process Trees

Define what they are, provide examples and anomalies.

* Process Path vs Process Tree

## Data sources
* Process, Process_Path, Process_Summary, Process_Uber_Summary
* Critical features: PID_HASH, PARENT_PID_HASH

## Python APIs for creating them

### Create process paths
### Create process trees
* Given a dataset - load the whole thing
* Given a single process - load downward
* Given a set of processes - load downward
    * Get processes using:
        * process_name
        * process depth (as a way to avoid high-level trees)
        * other?
        * Whitelist of "SME" top levels: Explorer, Services, ?
