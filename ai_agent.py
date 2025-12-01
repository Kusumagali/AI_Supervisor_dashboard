import requests, time

SERVER = "https://YOUR-RENDER-URL.onrender.com"

print("🤖 AI Agent ready\n")

while True:
    cust = input("Customer ID: ")
    q = input("Question: ")

    res = requests.post(f"{SERVER}/requests", json={"customer_id": cust, "question": q}).json()
    req = res["request"]
    print("📨 Created request:", req["id"])

    while True:
        time.sleep(2)
        r = requests.get(f"{SERVER}/get_requests").json()
        for x in r:
            if x["id"] == req["id"] and x["status"] == "resolved":
                print("💬 Answer:", x["answer"], "\n")
                break
        else:
            continue
        break
