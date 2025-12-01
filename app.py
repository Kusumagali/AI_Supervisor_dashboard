from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
from datetime import datetime, timedelta, timezone
import uuid, threading, os
import sqlite3

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")  # no async_mode

DB_FILE = "requests.db"
TIMEOUT_MINUTES = 5

# ------------------- DATABASE -------------------

def init_db():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS requests (
            id TEXT PRIMARY KEY,
            customer_id TEXT,
            question TEXT,
            answer TEXT,
            supervisor TEXT,
            status TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    return conn

conn = init_db()
cursor = conn.cursor()

def save_request(req):
    cursor.execute('''
        INSERT OR REPLACE INTO requests (id, customer_id, question, answer, supervisor, status, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (req["id"], req["customer_id"], req["question"], req["answer"], req["supervisor"], req["status"], req["timestamp"]))
    conn.commit()

def get_all_requests():
    cursor.execute("SELECT * FROM requests")
    rows = cursor.fetchall()
    keys = ["id", "customer_id", "question", "answer", "supervisor", "status", "timestamp"]
    return [dict(zip(keys, row)) for row in rows]

def get_request_by_question(question):
    cursor.execute("SELECT * FROM requests WHERE LOWER(question)=?", (question.lower(),))
    row = cursor.fetchone()
    if row:
        keys = ["id", "customer_id", "question", "answer", "supervisor", "status", "timestamp"]
        return dict(zip(keys, row))
    return None

def get_request_by_id(req_id):
    cursor.execute("SELECT * FROM requests WHERE id=?", (req_id,))
    row = cursor.fetchone()
    if row:
        keys = ["id", "customer_id", "question", "answer", "supervisor", "status", "timestamp"]
        return dict(zip(keys, row))
    return None

def update_request_db(req):
    cursor.execute('''
        UPDATE requests
        SET answer=?, supervisor=?, status=?
        WHERE id=?
    ''', (req["answer"], req["supervisor"], req["status"], req["id"]))
    conn.commit()

# ------------------- TIMEOUTS -------------------

def check_timeouts():
    while True:
        now = datetime.now(timezone.utc)
        requests = get_all_requests()
        for req in requests:
            if req["status"] == "pending":
                try:
                    created_time = datetime.fromisoformat(req["timestamp"])
                    if created_time.tzinfo is None:
                        created_time = created_time.replace(tzinfo=timezone.utc)
                    if now - created_time > timedelta(minutes=TIMEOUT_MINUTES):
                        req["status"] = "unresolved"
                        req["supervisor"] = "Timeout"
                        update_request_db(req)
                        socketio.emit("request_answered", req)
                except Exception as e:
                    print("Error checking timeout:", e)
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
        return "Hello! How can I help you?"
    return "Go to Supervisor Dashboard"

@app.route("/get_requests")
def get_requests():
    all_requests = sorted(get_all_requests(), key=lambda r: r["status"] != "pending")
    return jsonify(all_requests)

@app.route("/requests", methods=["POST"])
def create_request():
    data = request.json
    customer_id = data.get("customer_id")
    question = data.get("question").strip()

    # Check AI knowledge
    ai_answered = get_request_by_question(question)
    if ai_answered and ai_answered["status"] == "resolved":
        new_req = {
            "id": str(uuid.uuid4()),
            "customer_id": customer_id,
            "question": question,
            "answer": ai_answered["answer"],
            "supervisor": "AI",
            "status": "resolved",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        save_request(new_req)
        socketio.emit("incoming_call", new_req)
        return jsonify({"message": "Answered by AI", "request": new_req})

    # Unknown → pending
    new_req = {
        "id": str(uuid.uuid4()),
        "customer_id": customer_id,
        "question": question,
        "answer": None,
        "supervisor": None,
        "status": "pending",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    save_request(new_req)
    socketio.emit("incoming_call", new_req)
    return jsonify({"message": "Request created", "request": new_req})

@app.route("/requests/<req_id>", methods=["PUT"])
def update_request(req_id):
    data = request.json
    answer = data.get("answer")
    supervisor = data.get("supervisor", "Supervisor")

    req = get_request_by_id(req_id)
    if not req:
        return jsonify({"error": "Request not found"}), 404

    req["answer"] = answer
    req["supervisor"] = supervisor
    req["status"] = "resolved"
    update_request_db(req)
    socketio.emit("request_answered", req)
    return jsonify({"message": "Request updated", "request": req})

# ------------------- MAIN -------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port, allow_unsafe_werkzeug=True)
