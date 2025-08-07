from flask import Flask, request, jsonify
import requests

app = Flask(__name__, static_url_path='/static')  # This enables /static/ access by default

# IBM Watson credentials
API_KEY = "Fn6si-el8bo8bnniDAygBaWupNpOfnZHoGAU1oMADB1I"
ENDPOINT_URL = "https://us-south.ml.cloud.ibm.com/ml/v4/deployments/e4a2433d-2f41-4875-a1b0-d56caa26884f/ai_service?version=2021-05-01"

def get_ibm_token():
    response = requests.post(
        "https://iam.cloud.ibm.com/identity/token",
        data={"apikey": API_KEY, "grant_type": "urn:ibm:params:oauth:grant-type:apikey"},
    )
    return response.json()["access_token"]

mltoken = get_ibm_token()

@app.route("/")
def index():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    payload = {
        "messages": [{"role": "user", "content": user_message}]
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {mltoken}"
    }

    response = requests.post(ENDPOINT_URL, json=payload, headers=headers)

    try:
        response_json = response.json()
        reply = response_json["choices"][0]["message"]["content"]
        return jsonify({"reply": reply})

    except ValueError:
        return jsonify({"error": "Invalid JSON in response", "raw": response.text}), 500
    except Exception as e:
        return jsonify({"error": str(e), "raw": response.text}), 500

if __name__ == "__main__":
    app.run(debug=True)
