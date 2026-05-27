import json
import csv

FILE = "/home/intileo/Desktop/wren-ai/WrenAI/docker/crm_mdl1_copied.json"
CSV_FILE = "/home/intileo/Desktop/wren-ai/WrenAI/docker/column_descriptions.csv"

# Load CSV into dict: { "TableName": { "columnName": "description" } }
csv_descriptions = {}
with open(CSV_FILE, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        table = row['table_name'].strip()
        column = row['column_name'].strip()
        desc = row['description'].strip()
        if table not in csv_descriptions:
            csv_descriptions[table] = {}
        csv_descriptions[table][column] = desc

print(f"Loaded {sum(len(v) for v in csv_descriptions.values())} column descriptions for {len(csv_descriptions)} tables")

# Load MDL
with open(FILE) as f:
    data = json.load(f)

models = data.get('models', [])
updated_cols = 0
missing_cols = []
missing_tables = []

for m in models:
    display_name = m.get('display_name', '')
    table_name = display_name.split('.')[-1] if '.' in display_name else display_name

    if table_name not in csv_descriptions:
        missing_tables.append(table_name)
        continue

    table_col_descs = csv_descriptions[table_name]

    for col in m.get('columns', []):
        col_name = col.get('reference_name', '')
        if col_name not in table_col_descs:
            missing_cols.append(f"{table_name}.{col_name}")
            continue

        props = col.get('properties', {})
        if isinstance(props, str):
            props = json.loads(props)
            col['properties'] = json.dumps({**props, 'description': table_col_descs[col_name]})
        else:
            props['description'] = table_col_descs[col_name]
            col['properties'] = props

        updated_cols += 1

# Save
with open(FILE, 'w') as f:
    json.dump(data, f, indent=2)

print(f"✅ Done! Updated {updated_cols} column descriptions.")

if missing_tables:
    print(f"\n⚠️  Tables in MDL but not in CSV ({len(missing_tables)}):")
    for t in missing_tables:
        print(f"   - {t}")

if missing_cols:
    print(f"\n⚠️  Columns in MDL but not in CSV ({len(missing_cols)}):")
    for c in missing_cols:
        print(f"   - {c}")
