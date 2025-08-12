from flask import Blueprint, request, jsonify
from models.manual import insert_manual
import PyPDF2
import io

ingest_bp = Blueprint("ingest", __name__)

@ingest_bp.route("/", methods=["POST"])
def ingest():
    if 'file' not in request.files:
        return jsonify({"error": "PDF file required"}), 400

    file = request.files['file']
    model = request.form.get('model', 'General')  # Default to 'General' if not provided

    # Read and extract text from PDF
    pdf_reader = PyPDF2.PdfReader(file)
    content = ""
    for page in pdf_reader.pages:
        content += page.extract_text() or ""

    manual_data = {"model": model, "content": content}
    result = insert_manual(manual_data)
    return jsonify({"inserted_id": str(result.inserted_id)})