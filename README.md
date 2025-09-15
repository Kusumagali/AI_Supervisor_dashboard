# AI Supervisor Dashboard

A human-in-the-loop system where an AI handles customer questions and escalates to a human supervisor when needed. Built with Python, Flask, and SocketIO.


## Project Structure

├── app.py # Flask backend + supervisor dashboard
├── ai_agent.py # AI agent that handles customer questions
├── requirements.txt # Python dependencies
├── templates/
│ ├── index.html # Landing page
│ └── dashboard.html # Supervisor dashboard
├── README.md # This file
└── .gitignore # Ignore venv, pycache, requests.json



# Setup Instructions
Clone the repository
git clone https://github.com/Kusumagali/AI_Supervisor_dashboard.git
cd AI_Supervisor_dashboard


Create virtual environment
python -m venv venv
Activate virtual environment

Windows: venv\Scripts\activate

Mac/Linux: source venv/bin/activate

Install dependencies
pip install -r requirements.txt


Run the server
python app.py
Run the AI agent
python ai_agent.py
Open the dashboard
Visit: http://127.0.0.1:5000/dashboard

# Features
AI answers customer questions automatically if known.

Unanswered questions escalate to a human supervisor.

Supervisor can respond via dashboard.

Requests update in real-time using SocketIO.

Request lifecycle: Pending → Resolved / Unresolved.

Knowledge base updates automatically for repeated questions.

Optional notifications and sound alerts for new requests.

# Design Notes
AI Agent: Polls and sends questions to the server, checks knowledge base.

Supervisor Dashboard: Displays all requests, allows answering pending ones.

Data Storage: requests.json (auto-generated) keeps track of requests.

Scaling: Modular code allows scaling to hundreds of requests per day.

# Next Steps / Improvements:

Integrate real phone/text input (e.g., Twilio).

Use a database instead of JSON for persistence.

Add user authentication for supervisors.


