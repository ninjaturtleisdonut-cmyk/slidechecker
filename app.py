from flask_cors import CORS
from flask import Flask, request, jsonify
import requests, os

app = Flask(__name__)
CORS(app)

HF_API_KEY = os.environ.get("HF_API_KEY")

MODELS = [
    "google/flan-t5-base",
    "facebook/bart-large-cnn",
    "tiiuae/falcon-7b-instruct"
]

def send_to_huggingface(prompt):
    HF_API_KEY = os.environ.get("HF_API_KEY")
    headers = {
        "Authorization": f"Bearer {HF_API_KEY}",
        "Content-Type": "application/json"
    }

    for model in MODELS:
        try:
            url = f"https://api-inference.huggingface.co/models/{model}"
            response = requests.post(
                url,
                headers=headers,
                json={"inputs": prompt},
                timeout=60
            )

            if response.status_code == 200:
                output = response.json()
                if isinstance(output, list):
                    return output[0].get("generated_text", "")
                return str(output)

        except Exception:
            continue

    return "AI temporarily unavailable. Please try again."

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

