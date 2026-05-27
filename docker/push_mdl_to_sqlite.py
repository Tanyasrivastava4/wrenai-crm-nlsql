import json
import sqlite3

MDL_FILE = "/home/intileo/Desktop/wren-ai/WrenAI/docker/crm_mdl1_copied.json"
SQLITE_FILE = "/home/intileo/Desktop/wren-ai/WrenAI/docker/wren_db_new.sqlite3"
PROJECT_ID = 6

# Load MDL
with open(MDL_FILE) as f:
    data = json.load(f)

models = data.get('models', [])

conn = sqlite3.connect(SQLITE_FILE)
cur = conn.cursor()

# Check current state
cur.execute("SELECT COUNT(*) FROM model WHERE project_id = ?", (PROJECT_ID,))
print(f"Current models in SQLite: {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM model_column WHERE model_id IN (SELECT id FROM model WHERE project_id = ?)", (PROJECT_ID,))
print(f"Current columns in SQLite: {cur.fetchone()[0]}")

# Delete old data
cur.execute("DELETE FROM model_column WHERE model_id IN (SELECT id FROM model WHERE project_id = ?)", (PROJECT_ID,))
cur.execute("DELETE FROM model WHERE project_id = ?", (PROJECT_ID,))
conn.commit()
print("\nDeleted old data.")

# Insert new models and columns
inserted_models = 0
inserted_cols = 0

for m in models:
    props = m.get('properties', '{}')
    if isinstance(props, dict):
        props = json.dumps(props)

    # Ensure displayName is in properties
    p = json.loads(props)
    p['displayName'] = m.get('display_name', '')
    props = json.dumps(p)

    cur.execute("""
        INSERT INTO model (id, project_id, display_name, source_table_name, reference_name, 
                          ref_sql, cached, refresh_time, properties, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        m['id'], PROJECT_ID,
        m.get('display_name'), m.get('source_table_name'),
        m.get('reference_name'), m.get('ref_sql'),
        m.get('cached', 0), m.get('refresh_time'),
        props,
        m.get('created_at', '2026-04-18 07:35:26'),
        m.get('updated_at', '2026-04-18 07:35:26')
    ))
    inserted_models += 1

    for col in m.get('columns', []):
        col_props = col.get('properties', '{}')
        if isinstance(col_props, dict):
            col_props = json.dumps(col_props)

        cur.execute("""
            INSERT INTO model_column (id, model_id, is_calculated, display_name, source_column_name,
                                     reference_name, aggregation, lineage, type, not_null, is_pk,
                                     properties, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            col['id'], col['model_id'],
            col.get('is_calculated', 0),
            col.get('display_name'), col.get('source_column_name'),
            col.get('reference_name'), col.get('aggregation'),
            col.get('lineage'), col.get('type'),
            col.get('not_null', 0), col.get('is_pk', 0),
            col_props,
            col.get('created_at', '2026-04-18 07:35:26'),
            col.get('updated_at', '2026-04-18 07:35:26')
        ))
        inserted_cols += 1

conn.commit()
conn.close()

print(f"✅ Done!")
print(f"   Models inserted: {inserted_models}")
print(f"   Columns inserted: {inserted_cols}")
