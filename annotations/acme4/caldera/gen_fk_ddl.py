import json

with open('caldera_report_schema.json', 'r') as f:
    schema = json.load(f)

for table_name, table_info in schema['tables'].items():
    parent = table_info.get('parent', 'None')
    print(f"{table_name:<60} parent: {parent}")
    print(f"")


for table_name, table_info in schema['tables'].items():
    parent = table_info.get('parent')
    if parent and '_dlt_parent_id' in table_info.get('columns', {}):
        print(f"COMMENT ON COLUMN {table_name}._dlt_parent_id IS 'FK to {parent}._dlt_id';")