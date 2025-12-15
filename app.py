from flask_cors import CORS
from flask import Flask, request, jsonify
import requests, os

app = Flask(__name__)
CORS(app)

HF_API_KEY = os.environ.get("HF_API_KEY")

def send_to_huggingface(prompt):
    url = "https://api-inference.huggingface.co/models/google/flan-t5-large"
    headers = {
        "Authorization": f"Bearer {HF_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 400,
            "temperature": 0.2,
            "return_full_text": False
        }
    }

    response = requests.post(url, headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    output = response.json()
    if isinstance(output, list):
        return output[0].get("generated_text", "")
    return str(output)

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
        result = send_to_huggingface(prompt)
        return jsonify({"report": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

