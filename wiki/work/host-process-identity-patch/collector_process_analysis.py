"""Independent collector identity/visibility oracle over normal raw process rows."""
from experiment_live_analysis import digest


def collector_checks(connection, provenance, host_provenance, agent):
    pid = provenance['pid']
    birth = (116444736000000000 + host_provenance['boot_unix_seconds'] * 10_000_000
             + provenance['start_ticks'] * 10_000_000 // provenance['clock_ticks'])
    expected = digest(host_provenance['hostname'].strip().upper(), pid, birth)
    cursor = connection.execute('select * from process where pid=?', [pid])
    columns = [d[0].lower() for d in cursor.description]
    rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
    refreshes = [r for r in rows if r['activitytype'] == 'Refresh']
    return dict(pid=pid, expected_birth_filetime=birth, expected_pid_hash=expected,
                rows=rows, gates=dict(
                    collector_refresh_recorded=bool(refreshes),
                    collector_preexisting_not_fabricated_start=bool(rows) and not any(r['activitytype'] == 'Start' for r in rows),
                    collector_canonical_identity=bool(rows) and all(r['pidhash'] == expected for r in rows),
                    collector_refresh_uses_actual_birth=bool(refreshes) and all(r['eventtime'] == birth for r in refreshes),
                    collector_agent_matches=bool(rows) and all(r['agentid'] == agent for r in rows),
                    collector_executable_matches=bool(refreshes) and all(r['processpath'] == provenance['executable'] for r in refreshes),
                    collector_commandline_matches=bool(refreshes) and all(r['commandline'] == provenance['commandline'] for r in refreshes),
                    collector_parent_pid_matches=bool(refreshes) and all(r['parentpid'] == provenance['parent_pid'] for r in refreshes),
                    collector_user_recorded=bool(refreshes) and all(r.get('username') and not r['username'].lower().startswith('unknown') for r in refreshes)))
