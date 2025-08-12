from flask import Blueprint, request, jsonify
from utils.gemini import ask_gemini
from models.manual import find_manual

qa_bp = Blueprint("qa", __name__)

@qa_bp.route("/", methods=["POST"])
def ask():
    data = request.json
    question = data.get("question")
    model = data.get("model")
    # Find relevant manual section (simplified)
    manual = find_manual({"model": model})
    context = manual.get("content", "") if manual else ""
    answer = ask_gemini(question, context)
    return jsonify({"answer": answer})