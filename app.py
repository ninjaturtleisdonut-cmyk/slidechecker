from flask import Flask, request, jsonify
import requests, os

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def send_to_gemini(prompt):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    params = {"key": GEMINI_API_KEY}
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts":[{"text":prompt}]}]
    }

    r = requests.post(url, headers=headers, params=params, json=payload)
    r.raise_for_status()
    return r.json()["candidates"][0]["content"]["parts"][0]["text"]

@app.route("/analyze", methods=["POST"])
def analyze():
    text = request.json.get("text","")
    if not text:
        return jsonify({"error":"No text"}), 400

    prompt = f"""
You are an expert presentation reviewer.

Return:
1. One sentence summary
2. Bullet list of problems
3. A CHECKLIST

Slide text:
{text}
"""
    try:
        result = send_to_gemini(prompt)
        return jsonify({"report": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

app.run(host="0.0.0.0", port=8080)
