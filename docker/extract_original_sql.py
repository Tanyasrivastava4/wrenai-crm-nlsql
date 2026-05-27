import urllib.request
import urllib.error
import json
import time
import sqlite3

# ── CONFIG ──────────────────────────────────────────────────────────
WRENAI_URL  = "http://localhost:5555"
WRENUI_URL  = "http://localhost:3001"
MDL_HASH    = "112352e84310fe94aa2ad9f1ef7d5505fa991795"
SQLITE_PATH = "/home/intileo/Desktop/wren-ai/WrenAI/docker/wren_db_current.sqlite3"
# ────────────────────────────────────────────────────────────────────


def step1_ask_question(question):
    """
    STEP 1: Send question to wren-ai-service
    
    CALLS:   POST http://localhost:5555/v1/asks
    SENDS:   { query, id (MDL hash) }
    RETURNS: query_id (UUID string)
    """
    print(f"\n  [STEP 1] Sending question to wren-ai-service...")
    print(f"           URL: POST {WRENAI_URL}/v1/asks")

    payload = json.dumps({
        "query": question,
        "id": MDL_HASH
    }).encode()

    req = urllib.request.Request(
        f"{WRENAI_URL}/v1/asks",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    response = urllib.request.urlopen(req)
    result   = json.loads(response.read())
    query_id = result.get("query_id") or result.get("queryId")

    print(f"           RESPONSE: query_id = {query_id}")
    return query_id


def step2_poll_until_finished(query_id):
    """
    STEP 2: Keep polling until wren-ai-service finishes
    
    CALLS:   GET http://localhost:5555/v1/asks/{query_id}
    RETURNS: wren_sql (the fake virtual table SQL)
    """
    print(f"\n  [STEP 2] Polling wren-ai-service until finished...")
    print(f"           URL: GET {WRENAI_URL}/v1/asks/{query_id}")

    for attempt in range(20):
        time.sleep(3)
        print(f"           Attempt {attempt+1}...", end=" ")

        req      = urllib.request.Request(f"{WRENAI_URL}/v1/asks/{query_id}")
        response = urllib.request.urlopen(req)
        result   = json.loads(response.read())
        status   = result.get("status", "")

        print(f"status = {status}")

        if status == "finished":
            # extract the Wren SQL from response
            wren_sql = None
            if result.get("response"):
                wren_sql = result["response"][0]["sql"]

            print(f"\n           ✅ WREN SQL (cannot run on MySQL directly):")
            print(f"           {wren_sql}")
            return wren_sql

        if status == "failed":
            error = result.get("error", {})
            raise Exception(f"wren-ai-service failed: {error}")

    raise Exception("TIMEOUT: wren-ai-service did not finish in time")


def step3_get_response_id(query_id):
    """
    STEP 3: Look up SQLite to get the integer responseId
    
    NOT an API call — direct SQLite file read
    
    READS:   asking_task table WHERE uuid = query_id
    RETURNS: thread_response_id (integer like 9, 10, 11...)
    
    WHY NEEDED?
      wren-ai-service gives us a UUID (query_id)
      but GraphQL needs an INTEGER (responseId)
      SQLite links them: asking_task.uuid → thread_response_id
    """
    print(f"\n  [STEP 3] Looking up SQLite for responseId...")
    print(f"           FILE: {SQLITE_PATH}")
    print(f"           QUERY: SELECT thread_response_id FROM asking_task WHERE uuid='{query_id}'")

    # wait a moment for wren-ui to save to SQLite
    time.sleep(2)

    db  = sqlite3.connect(SQLITE_PATH)
    row = db.execute(
        "SELECT thread_response_id FROM asking_task WHERE uuid = ?",
        (query_id,)
    ).fetchone()
    db.close()

    if not row:
        raise Exception(f"responseId not found in SQLite for query_id: {query_id}")

    response_id = row[0]
    print(f"           RESULT: responseId = {response_id}")
    return response_id


def step4_get_original_sql(response_id):
    """
    STEP 4: Call wren-ui GraphQL to get Original MySQL SQL
    
    CALLS:   POST http://localhost:3001/api/graphql
    SENDS:   { operationName: GetNativeSQL, variables: { responseId } }
    
    INSIDE GraphQL (what happens internally):
      A) Gets Wren SQL from SQLite:
         SELECT sql FROM thread_response WHERE id = responseId
      
      B) Gets MDL Manifest from SQLite:
         SELECT manifest FROM deploy_log WHERE status='SUCCESS'
         (421,939 chars — complete map of all 115 tables)
      
      C) Calls wren-engine with Wren SQL + Manifest:
         POST http://wren-engine:8080/v1/statement
         { sql: wren_sql, manifest: mdl_manifest, dialect: "mysql" }
      
      D) wren-engine translates:
         virtual table names → real MySQL table names
         wraps in subquery with real column names
      
      E) Returns Original MySQL SQL back to us
    
    RETURNS: original_sql (real MySQL executable SQL)
    """
    print(f"\n  [STEP 4] Calling wren-ui GraphQL for Original SQL...")
    print(f"           URL: POST {WRENUI_URL}/api/graphql")
    print(f"           OPERATION: nativeSql(responseId: {response_id})")
    print(f"           INTERNALLY GraphQL will:")
    print(f"             A) Get Wren SQL from SQLite thread_response id={response_id}")
    print(f"             B) Get MDL Manifest from SQLite deploy_log")
    print(f"             C) Send both to wren-engine for translation")
    print(f"             D) Return real MySQL SQL")

    graphql_query = {
        "operationName": "GetNativeSQL",
        "query": "query GetNativeSQL($responseId: Int!) { nativeSql(responseId: $responseId) }",
        "variables": {"responseId": response_id}
    }

    payload = json.dumps(graphql_query).encode()

    req = urllib.request.Request(
        f"{WRENUI_URL}/api/graphql",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    response    = urllib.request.urlopen(req)
    result      = json.loads(response.read())
    original_sql = result["data"]["nativeSql"]

    print(f"\n           ✅ ORIGINAL SQL (runs directly on MySQL):")
    # print first 200 chars so it doesn't flood terminal
    print(f"           {original_sql[:200]}...")
    return original_sql


def step5_send_to_crm_team(question, wren_sql, original_sql, client_db):
    """
    STEP 5: Package everything and send to CRM team
    
    In real system this would be:
      POST https://crm-server.com/webhook/result
      { question, sql, status }
    
    Here we just print what would be sent
    """
    print(f"\n  [STEP 5] Packaging result for CRM team...")
    print(f"           (In real system: POST to CRM webhook URL)")

    # replace source db name with client's db name if different
    final_sql = original_sql.replace("crm_r_tech_solution_101", client_db)

    output = {
        "status":       "success",
        "question":     question,
        "client_db":    client_db,
        "wren_sql":     wren_sql,      # ← fake SQL (for reference only)
        "original_sql": final_sql      # ← real SQL (send THIS to CRM team)
    }

    return output


def run_pipeline(question, client_db="crm_r_tech_solution_101"):
    """
    COMPLETE PIPELINE — runs all 5 steps for one question
    """
    print(f"\n{'='*65}")
    print(f"  QUESTION : {question}")
    print(f"  CLIENT DB: {client_db}")
    print(f"{'='*65}")

    try:
        # STEP 1 — ask wren-ai-service
        query_id = step1_ask_question(question)

        # STEP 2 — poll until finished, get Wren SQL
        wren_sql = step2_poll_until_finished(query_id)

        # STEP 3 — get integer responseId from SQLite
        response_id = step3_get_response_id(query_id)

        # STEP 4 — get Original SQL via GraphQL
        original_sql = step4_get_original_sql(response_id)

        # STEP 5 — package for CRM team
        output = step5_send_to_crm_team(question, wren_sql, original_sql, client_db)

        # ── FINAL COMPARISON ──────────────────────────────────────
        print(f"\n{'─'*65}")
        print(f"  FINAL RESULT COMPARISON")
        print(f"{'─'*65}")

        print(f"\n  ❌ WREN SQL (cannot run on MySQL — virtual table names):")
        print(f"  {output['wren_sql']}")

        print(f"\n  ✅ ORIGINAL SQL (send THIS to CRM team — runs on MySQL):")
        print(f"  {output['original_sql'][:300]}...")

        print(f"\n  📦 FULL JSON TO SEND TO CRM TEAM VIA WEBHOOK:")
        # show summary (original_sql is too long to print fully)
        summary = dict(output)
        summary["original_sql"] = output["original_sql"][:200] + "... (truncated)"
        print(json.dumps(summary, indent=4))

        return output

    except Exception as e:
        print(f"\n  ❌ ERROR: {e}")
        return None


# ── RUN TESTS ────────────────────────────────────────────────────────

print("\n" + "★"*65)
print("  WRENAI PIPELINE TEST — Wren SQL vs Original SQL")
print("★"*65)

# Test 1 — simple count query
run_pipeline(
    question   = "how many deals are there?",
    client_db  = "crm_r_tech_solution_101"
)

# uncomment below to test more questions
# (embedding model must be working)

# run_pipeline(
#     question  = "show all pipeline stages",
#     client_db = "crm_r_tech_solution_101"
# )

# run_pipeline(
#     question  = "show all leads with their title and status",
#     client_db = "crm_r_tech_solution_102"   # different client db
# )