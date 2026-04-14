from flask import Flask, jsonify, make_response, render_template, request

from services.pdf_export import build_summary_pdf
from services.summary_service import generate_summary
from services.text_utils import load_env_file, normalize_whitespace, word_count


load_env_file()

app = Flask(__name__)

VALID_LENGTHS = {"short", "medium", "long"}
MAX_INPUT_CHARS = 50000


def _request_payload() -> dict:
    if request.content_type and "multipart/form-data" in request.content_type:
        uploaded_file = request.files.get("file")
        text = request.form.get("text", "")

        if uploaded_file and uploaded_file.filename:
            if not uploaded_file.filename.lower().endswith(".txt"):
                return {"error": "Only plain .txt files are supported for upload."}
            text = uploaded_file.stream.read().decode("utf-8", errors="ignore")

        return {"text": text, "length": request.form.get("length", "medium")}

    return request.get_json(silent=True) or {}


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/summarize", methods=["POST"])
def summarize():
    payload = _request_payload()
    if payload.get("error"):
        return jsonify({"error": payload["error"]}), 400

    text = normalize_whitespace(payload.get("text") or "")
    length = (payload.get("length") or "medium").strip().lower()

    if length not in VALID_LENGTHS:
        return jsonify({"error": "Choose a valid summary length: short, medium, or long."}), 400

    if len(text) > MAX_INPUT_CHARS:
        return (
            jsonify(
                {
                    "error": f"Please keep the input under {MAX_INPUT_CHARS:,} characters so the summary can be processed reliably."
                }
            ),
            400,
        )

    if len(text) < 120 or word_count(text) < 25:
        return (
            jsonify(
                {
                    "error": "Enter a longer passage with at least 120 characters and 25 words so the summary can preserve the key ideas."
                }
            ),
            400,
        )

    result = generate_summary(text, length)

    if result["output_word_count"] >= result["input_word_count"]:
        return jsonify({"error": "The generated summary was not shorter than the original text. Please try different text."}), 500

    return jsonify(result)


@app.route("/download-summary", methods=["POST"])
def download_summary():
    payload = request.get_json(silent=True) or {}
    summary = normalize_whitespace(payload.get("summary") or "")
    length = (payload.get("length") or "medium").strip().lower()

    if not summary:
        return jsonify({"error": "Generate a summary before downloading a PDF."}), 400

    pdf_bytes = build_summary_pdf(summary, length if length in VALID_LENGTHS else "medium")
    response = make_response(pdf_bytes)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = "attachment; filename=story-summary.pdf"
    return response


if __name__ == "__main__":
    app.run(debug=True)
