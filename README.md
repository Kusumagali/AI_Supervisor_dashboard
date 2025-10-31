# AI Supervisor Dashboard  
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/Flask-WebFramework-green)
![NLP](https://img.shields.io/badge/NLP-Rule--Based-lightgrey)
![JSON](https://img.shields.io/badge/JSON-DataStorage-yellow)

## 🧠 Project Overview  
The **AI Supervisor Dashboard** is a Flask-based web application used for **automated customer query handling**.  
It uses a **rule-based NLP system** to detect known questions and reply automatically.  
Unresolved or unknown questions are **marked for supervisor review**.  

Instead of using MySQL, the project stores data in **JSON files**, making it lightweight and easy to deploy without external databases.

## 🧰 Tech Stack  
- Python  
- Flask (Web Framework)  
- JSON (for storing and updating support data)  
- HTML + CSS (Frontend UI)

## 🔍 Key Features  
- ✅ Automatically replies to known questions using rule-based NLP  
- ✅ Stores user queries and responses in JSON files  
- ✅ Supervisor dashboard to view and resolve flagged queries  
- ✅ Lightweight — no database setup required  
- ✅ Good for demonstrating **backend + logic + UI integration**

## 🚀 What I Did  
- Implemented a **keyword-based NLP matching system** to auto-reply common queries.  
- Stored queries, responses, and status in structured **JSON dictionaries**.  
- Developed the Flask web interface for:
  - Submitting queries
  - Viewing unresolved requests
  - Supervisor resolving flagged issues  
- Created a simple and clean HTML/CSS UI for usability.  

## 🛠 How to Run  

### 1. Clone the Repository  
```bash
git clone https://github.com/Kusumagali/AI_Supervisor_dashboard.git
cd AI_Supervisor_dashboard
pip install -r requirements.txt

```
## Run the Application
python app.py

## Open in Browser
http://localhost:5000


