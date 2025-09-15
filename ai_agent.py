import json, os, time, uuid, requests, threading
from datetime import datetime, timezone

DATA_FILE = "requests.json"
SERVER_URL = "http://127.0.0.1:5000"

# Load existing requests
def load_requests():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return {r["id"]: r for r in json.load(f)}
        except:
            return {}
    return {}

requests_store = load_requests()
lock = threading.Lock()

# Function to poll a request until answered
def poll_request(req_id):
    while True:
        time.sleep(2)
        with lock:
            try:
                with open(DATA_FILE, "r") as f:
                    requests_store.update({r["id"]: r for r in json.load(f)})
            except:
                continue
            r_status = requests_store.get(req_id)
            if r_status and r_status["status"] in ["resolved", "unresolved"]:
                print(f"\n✅ Request answered: {r_status.get('answer','N/A')} (Status: {r_status['status']})\n")
                break

print("🟢 AI Agent running. Type 'exit' to quit.\n")

while True:
    customer_id = input("Customer ID (type 'exit' to quit): ")
    if customer_id.lower() == "exit":
        break
    question = input("Customer asks: ")
    if question.lower() == "exit":
        break

    # Check knowledge base
    found = False
    with lock:
        for r in requests_store.values():
            if r["question"].lower() == question.lower() and r["status"] == "resolved":
                print(f"✅ Already answered: {r['answer']}\n")
                found = True
                break
    if found:
        continue

    # Submit new request
    payload = {"customer_id": customer_id, "question": question}
    try:
        res = requests.post(f"{SERVER_URL}/requests", json=payload).json()
        req = res["request"]
        print(f"✅ Request {req['id']} created for customer {customer_id}")
        print("📩 Waiting for supervisor or AI to answer...\n")

        # Start polling in a separate thread
        threading.Thread(target=poll_request, args=(req["id"],), daemon=True).start()

    except Exception as e:
        print("❌ Error creating request:", e, "\n")
