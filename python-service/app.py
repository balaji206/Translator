from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename
from PIL import Image
import pytesseract
import PyPDF2
import re
from transformers import MarianMTModel, MarianTokenizer, pipeline

# ------------------------
# Flask setup
# ------------------------
app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ------------------------
# Load small multilingual Hugging Face model (~310MB)
# ------------------------
MODEL_NAME = "Helsinki-NLP/opus-mt-mul-en"
tokenizer = MarianTokenizer.from_pretrained(MODEL_NAME)
model = MarianMTModel.from_pretrained(MODEL_NAME)
translator = pipeline("translation", model=model, tokenizer=tokenizer)

# ------------------------
# Utility functions
# ------------------------
def clean_text(text):
    """Remove control characters and extra spaces/newlines"""
    text = re.sub(r'[\x00-\x1F\x7F]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def segment_text_nep(text):
    """Heuristic segmentation for Nepali text"""
    text = text.replace("।", "। ")
    text = re.sub(r'([क-ह])([क-ह])', r'\1 \2', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def segment_text_si(text):
    """Heuristic segmentation for Sinhala text"""
    # Simple split on spaces for now (can be improved)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def translate_text(text, source_lang):
    """Segment and translate text"""
    if source_lang in ["ne", "nep"]:
        text = segment_text_nep(text)
    elif source_lang in ["si", "sin"]:
        text = segment_text_si(text)
    
    if not text:
        return ""
    translated = translator(text, max_length=512)
    return translated[0]["translation_text"]

# ------------------------
# Routes
# ------------------------
@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "Python service running"}), 200

@app.route("/extract-text", methods=["POST"])
def extract_text_route():
    source_lang = request.form.get("source_lang", "ne").lower()
    if source_lang not in ["ne", "nep", "si", "sin"]:
        return jsonify({"error": "Unsupported source_lang. Use 'ne', 'nep', 'si', or 'sin'."}), 400

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    extracted_text = ""
    try:
        # Extract text from PDF
        if filename.lower().endswith(".pdf"):
            with open(filepath, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        extracted_text += page_text + "\n"
        else:
            # OCR for images
            ocr_lang = "nep" if source_lang in ["ne", "nep"] else "sin"
            image = Image.open(filepath)
            extracted_text = pytesseract.image_to_string(image, lang=ocr_lang)

        # Clean extracted text
        extracted_text = clean_text(extracted_text)
        if not extracted_text:
            return jsonify({"error": "No text detected"}), 400

        # Translate
        translated_text = translate_text(extracted_text, source_lang)

        return jsonify({
            "source_lang": source_lang,
            "extracted_text": extracted_text,
            "translated_text": translated_text
        })

    finally:
        if os.path.exists(filepath):
            os.remove(filepath)

# ------------------------
# Run server
# ------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
