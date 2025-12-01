from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
from datetime import datetime, timedelta, timezone
import uuid, json, threading, os

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")  # no async_mode

DATA_FILE = "requests.json"
TIMEOUT_MINUTES = 5

# Load existing requests
try:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            requests_store = {r["id"]: r for r in json.load(f)}
    else:
        requests_store = {}
except (json.JSONDecodeError, FileNotFoundError):
    requests_store = {}

def save_requests():
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(list(requests_store.values()), f, indent=4)
    except Exception as e:
        print("Error saving requests:", e)

def check_timeouts():
    while True:
        now = datetime.now(timezone.utc)
        for req in requests_store.values():
            if req["status"] == "pending":
                try:
                    created_time = datetime.fromisoformat(req["timestamp"])
                    if created_time.tzinfo is None:
                        created_time = created_time.replace(tzinfo=timezone.utc)
                    if now - created_time > timedelta(minutes=TIMEOUT_MINUTES):
                        req["status"] = "unresolved"
                        req["supervisor"] = "Timeout"
                        save_requests()
                        socketio.emit("request_answered", req)
                except Exception as e:
                    print("Error checking request timeout:", e)
        socketio.sleep(30)

threading.Thread(target=check_timeouts, daemon=True).start()

# ------------------- ROUTES -------------------

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/ask", methods=["POST"])
def ask():
    question = request.form.get("question")
    if question.lower() in ["hi", "hello"]:
        answer = "Hello! How can I help you?"
    else:
        answer = "Go to Supervisor Dashboard"
    return answer

@app.route("/get_requests")
def get_requests():
    all_requests = sorted(requests_store.values(), key=lambda r: r["status"] != "pending")
    return jsonify(all_requests)

@app.route("/requests", methods=["POST"])
def create_request():
    data = request.json
    customer_id = data.get("customer_id")
    question = data.get("question")
    normalized_question = question.strip().lower()

    # Check AI knowledge
    for r in requests_store.values():
        if r["question"].strip().lower() == normalized_question and r["status"] == "resolved":
            new_request = {
                "id": str(uuid.uuid4()),
                "customer_id": customer_id,
                "question": question,
                "answer": r["answer"],
                "supervisor": "AI",
                "status": "resolved",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            requests_store[new_request["id"]] = new_request
            save_requests()
            socketio.emit("incoming_call", new_request)
            return jsonify({"message": "Answered by AI", "request": new_request})

    # Unknown → pending
    req_id = str(uuid.uuid4())
    new_request = {
        "id": req_id,
        "customer_id": customer_id,
        "question": question,
        "answer": None,
        "supervisor": None,
        "status": "pending",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    requests_store[req_id] = new_request
    save_requests()
    socketio.emit("incoming_call", new_request)
    return jsonify({"message": "Request created", "request": new_request})

@app.route("/requests/<req_id>", methods=["PUT"])
def update_request(req_id):
    data = request.json
    answer = data.get("answer")
    supervisor = data.get("supervisor", "Supervisor")

    if req_id not in requests_store:
        return jsonify({"error": "Request not found"}), 404

    requests_store[req_id]["answer"] = answer
    requests_store[req_id]["supervisor"] = supervisor
    requests_store[req_id]["status"] = "resolved"
    save_requests()
    socketio.emit("request_answered", requests_store[req_id])
    return jsonify({"message": "Request updated", "request": requests_store[req_id]})

# ------------------- MAIN -------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # allow Werkzeug in production (Render)
    socketio.run(app, host="0.0.0.0", port=port, allow_unsafe_werkzeug=True)









