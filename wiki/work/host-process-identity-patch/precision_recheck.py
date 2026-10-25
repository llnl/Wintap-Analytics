"""Measure the current macro and an integer-only SQL alternative, read-only.

The alternative is diagnostic SQL, NOT a source macro change or relaxed gate.
Timestamp microsecond representability is separate from exact raw FILETIME.
"""
import json
from pathlib import Path

import duckdb
import jinja2


def main():
    root = Path(__file__).parent
    inputs = [('r7-replay','package_r7_analysis.json','package_r8_dbt_r7_replay.json'),
              ('r8-normal','package_r8_normal_analysis.json','package_r8_normal_dbt.json'),
              ('r8-shutdown','package_r8_shutdown_analysis.json','package_r8_shutdown_dbt.json')]
    macro = Path(__file__).resolve().parents[4]/'Wintappy/wintap_dbt/macros/time.sql'
    module = jinja2.Environment().from_string(macro.read_text()).module
    expr = module.win32_to_timestamp_expr('ft')
    results = []
    with duckdb.connect(':memory:') as c:
        cases = []
        for label, analysis_path, replay_path in inputs:
            analysis = json.loads((root/analysis_path).read_text())
            replay = json.loads((root/replay_path).read_text())
            for host in analysis['hosts']:
                for round_ in host['rounds']:
                    cases.append((label,host['host'],round_,replay))
        for label, host, round_, replay in cases:
            ft = round_['collector_process']['expected_birth_filetime']
            current, candidate = c.execute(f'''select
                epoch_us({expr})*10+116444736000000000,
                epoch_us(make_timestamp((ft-116444736000000000)//10))*10+116444736000000000
                from (select ?::bigint ft)''',[ft]).fetchone()
            built = next(r for r in replay if r['host']==host and r['round']==round_['name'])
            results.append(dict(capture_set=label,host=host,round=round_['name'],raw_filetime=ft,
                microsecond_representable=ft%10==0,current_macro_filetime=current,
                current_delta_ticks=current-ft,integer_alternative_filetime=candidate,
                integer_alternative_delta_ticks=candidate-ft,
                actual_dbt_exact_birth_passed=built['gates']['process_actual_birth_retained'],
                edge_tolerance_cannot_change_this_gate=True))
    (root/'package_r8_precision_recheck.json').write_text(json.dumps(results,indent=2)+'\n')
    print(json.dumps(results,indent=2))


if __name__ == '__main__':
    main()
