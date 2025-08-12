import requests
from config import GEMINI_API_KEY

def ask_gemini(question, context):
    # Use Gemini 1.5 Flash model
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [
            {"role": "user", "parts": [{"text": f"Context: {context}\nQuestion: {question}"}]}
        ]
    }
    print("Context sent to Gemini:", context)
    response = requests.post(url, json=payload)
    print("Gemini API response:", response.json())
    if response.ok:
        return response.json().get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
    return "Sorry, I couldn't find an answer."