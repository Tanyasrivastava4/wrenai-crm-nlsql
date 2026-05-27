#!/bin/bash
echo "=== WrenAI Startup Script ==="

# Step 1: Start containers
echo "Step 1: Starting containers..."
cd /home/intileo/Desktop/wren-ai/WrenAI/docker
docker compose up -d
sleep 60

# Step 2: Apply DocumentCleaner fix
echo "Step 2: Applying DocumentCleaner fix..."
cat > /tmp/fix_cleaner.py << 'PYEOF'
filepath = '/src/pipelines/indexing/__init__.py'
with open(filepath, 'r') as f:
    content = f.read()

# First clean up any duplicate try/except blocks
import re
broken = re.compile(
    r'            try:\n(?:                try:\n)*'
    r'                await store\.delete_documents\(filters\)\n'
    r'(?:            except Exception as e:\n'
    r'                logger\.warning\(f"Project ID: \{project_id\}, Skipping clean.*?\n)+',
    re.MULTILINE
)

correct = '''            try:
                await store.delete_documents(filters)
            except Exception as e:
                logger.warning(f"Project ID: {project_id}, Skipping clean - collection may not exist yet: {e}")
'''

new_content = broken.sub(correct, content)
if new_content != content:
    with open(filepath, 'w') as f:
        f.write(new_content)
    print('FIXED: DocumentCleaner patched')
else:
    print('Already correct - no changes needed')
PYEOF

docker cp /tmp/fix_cleaner.py wrenai-wren-ai-service-1:/tmp/fix_cleaner.py
docker exec wrenai-wren-ai-service-1 python3 /tmp/fix_cleaner.py

# Step 3: Restart service
echo "Step 3: Restarting wren-ai-service..."
docker restart wrenai-wren-ai-service-1 && sleep 30

# Step 4: Recreate deploy payload
echo "Step 4: Creating deploy payload..."
docker cp wrenai-wren-ui-1:/app/data/db.sqlite3 /tmp/wren_db.sqlite3
sqlite3 /tmp/wren_db.sqlite3 'SELECT manifest FROM deploy_log WHERE status="SUCCESS" ORDER BY id DESC LIMIT 1;' > /tmp/manifest.json
python3 -c "
import json
with open('/tmp/manifest.json') as f:
    manifest = json.load(f)
payload = {'mdl': manifest, 'id': '112352e84310fe94aa2ad9f1ef7d5505fa991795'}
with open('/tmp/deploy_payload.json', 'w') as f:
    json.dump(payload, f)
print('Payload ready')
"

# Step 5: Trigger deploy
echo "Step 5: Triggering deploy..."
curl -s -X POST http://localhost:5555/v1/semantics-preparations \
  -H "Content-Type: application/json" \
  -d @/tmp/deploy_payload.json

# Step 6: Wait for indexing
echo "Step 6: Waiting for indexing to complete..."
sleep 180

# Step 7: Verify Qdrant
echo "Step 7: Verifying Qdrant..."
docker exec wrenai-wren-ai-service-1 python3 -c "
import urllib.request, json
r = urllib.request.urlopen('http://qdrant:6333/collections/Document')
d = json.loads(r.read())
print('Document points:', d['result']['points_count'])
r = urllib.request.urlopen('http://qdrant:6333/collections/table_descriptions')
d = json.loads(r.read())
print('table_descriptions points:', d['result']['points_count'])
"

# Step 8: Test query
echo "Step 8: Testing query..."
QUERY_ID=$(curl -s -X POST http://localhost:5555/v1/asks \
  -H "Content-Type: application/json" \
  -d '{"query": "how many deals are there?", "mdl_hash": "112352e84310fe94aa2ad9f1ef7d5505fa991795"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['query_id'])")
echo "Query ID: $QUERY_ID"
sleep 45
curl -s http://localhost:5555/v1/asks/$QUERY_ID/result | python3 -c "
import sys,json
r=json.load(sys.stdin)
print('Status:', r['status'])
if r.get('response'):
    print('SQL:', r['response'][0]['sql'])
"

echo "=== WrenAI Startup Complete ==="
