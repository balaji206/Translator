# OCR & Translator API

This is a lightweight Flask-based API that can extract text from **images** and **PDFs** in **Nepali (`ne`)** and **Sinhala (`si`)**, and translate it into English using the free [LibreTranslate](https://libretranslate.com/) API.  

No PyTorch or Hugging Face tokens are required — fully free and easy to deploy.

---

## Features

- Extract text from **PDF** and **image files** using OCR (`pytesseract`).
- Translate Nepali and Sinhala text to English using a free online API.
- Minimal dependencies and easy setup.

---

## Requirements

- Python 3.10+
- pip packages:


- pip install flask pillow pytesseract PyPDF2 requests
- Tesseract OCR installed on your system.

### Usage

- Clone or download this repository.

- Make sure Tesseract is installed and available in your PATH.

### Run the Flask server:

- Copy code
- python app.py
- Send a POST request to /extract-text with:

- file: PDF or image (.png, .jpg, etc.)

- source_lang: "ne" for Nepali, "si" for Sinhala

##### Example using curl:

curl -X POST http://localhost:5000/extract-text \
  -F "file=@sample.pdf" \
  -F "source_lang=ne"
Response:

json
Copy code
{
  "source_lang": "ne",
  "extracted_text": "नमस्तेतेपाई कस् तेहुनहुन्छ",
  "translated_text": "Hello, how are you?"
}

##### Notes:

Supported languages: Nepali (ne) and Sinhala (si) only.

PDF extraction may fail for scanned PDFs — in that case, use an image-based PDF or convert to image first.

