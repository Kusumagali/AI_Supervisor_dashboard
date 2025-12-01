from flask import Flask, request, jsonify, send_from_directory
from flask_socketio import SocketIO
from datetime import datetime
import json, os, uuid

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')


DATA_FILE = "requests.json"

# Load stored requests
def load_requests():
    return json.load(open(DATA_FILE)) if os.path.exists(DATA_FILE) else []

# Save stored requests
def save_requests(data):
    json.dump(data, open(DATA_FILE, "w"))

requests_store = load_requests()

# Knowledge base (AI)
known_answers = {
    "what is your name": "I am AI Customer Assistant.",
    "what are your working hours": "We are open 24/7.",
    "how can i contact support": "You can contact support at support@example.com."
}

@app.route("/")
def dashboard():
    return send_from_directory("", "dashboard.html")

@app.route("/get_requests", methods=["GET"])
def get_requests():
    return jsonify(requests_store)

@app.route("/requests", methods=["POST"])
def create_request():
    data = request.json
    req_id = str(uuid.uuid4())

    question = data["question"].lower().strip()
    customer = data["customer_id"].strip()

    # AI auto-answer if known
    if question in known_answers:
        answer = known_answers[question]
        status = "resolved"
        supervisor = "AI"
    else:
        answer = ""
        status = "pending"
        supervisor = ""

    new_req = {
        "id": req_id,
        "customer_id": customer,
        "question": data["question"],
        "answer": answer,
        "supervisor": supervisor,
        "status": status,
        "timestamp": datetime.utcnow().isoformat()
    }

    requests_store.append(new_req)
    save_requests(requests_store)

    socketio.emit("incoming_request", new_req)
    return jsonify({"success": True, "request": new_req})


@app.route("/requests/<req_id>", methods=["PUT"])
def answer_request(req_id):
    data = request.json
    for r in requests_store:
        if r["id"] == req_id:
            r["answer"] = data["answer"]
            r["supervisor"] = "Supervisor"
            r["status"] = "resolved"
            save_requests(requests_store)
            socketio.emit("request_answered", r)
            return jsonify({"success": True, "updated": r})
    return jsonify({"success": False, "message": "Not found"}), 404


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

