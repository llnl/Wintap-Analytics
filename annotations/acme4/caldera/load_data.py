import dlt
from pathlib import Path
import json
import logging
import traceback
import os
import sys

logging.basicConfig(level=logging.DEBUG)
dlt.config['runtime.log_level'] = 'DEBUG'

pipeline = dlt.pipeline(
    pipeline_name="caldera",
    destination="duckdb",
    dataset_name="rpt",
    dev_mode=True
)


def _get_reports_dir() -> Path:
    # Allow overriding for different checkouts/machines.
    if len(sys.argv) > 1:
        return Path(sys.argv[1]).expanduser()
    return Path(os.environ.get("CALDERA_REPORT_DIR", "data/wintapv6/ACME4/caldera")).expanduser()

@dlt.source
def report_source():
    # Main table
    @dlt.resource(
        name="raw_report",
#        primary_key="uuid",
        write_disposition="replace",      # change to "append" or "merge" later
#        max_table_nesting=2,  # ✅ Stop deep nesting
    )
    def reports():
        obs_path = _get_reports_dir()
        for file in obs_path.glob("*.json"):
            print(f"Loading: {file}")
            with open(file) as f:
                report = json.load(f)
                # Transform the steps structure
                if 'steps' in report and isinstance(report['steps'], dict):
                    # Convert the dict with PAW keys into a list with PAW as a field
                    steps_list = []
                    for paw, paw_data in report['steps'].items():
                        paw_data['paw'] = paw  # Add PAW as a field
                        steps_list.append(paw_data)
                    
                    report['steps'] = steps_list
                
            # Handle skipped_abilities
            if 'skipped_abilities' in report and isinstance(report['skipped_abilities'], list):
                normalized_list = []
                for entry in report['skipped_abilities']:
                    if isinstance(entry, dict) and len(entry) == 1:
                        # Extract the single key (paw) and its value
                        paw = list(entry.keys())[0]
                        abilities = entry[paw]
                        normalized_list.append({
                            'paw': paw,
                            'abilities': abilities
                        })
                report['skipped_abilities'] = normalized_list

            yield report

    return reports()

# ------------------------------------------------------------------
# Run it
# ------------------------------------------------------------------
try:
    info = pipeline.run(report_source(),
#        loader_file_format="json",                # important for deep nesting
        # This hint is what creates one child table per metadata type

    )
    print(info)
except Exception as e:
    print(f"Pipeline crashed anyway: {e}")
    traceback.print_exc()
