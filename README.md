# Story Summary Studio

Story Summary Studio is a full-stack Flask web application that turns long text into shorter, cleaner summaries. It supports summary length selection, `.txt` uploads, dark mode, copy/export actions, speech-to-text input, downloadable PDFs, and local history in the browser.

## Features

- Long text summarization through `POST /summarize`
- Summary length options: `short`, `medium`, `long`
- OpenAI-backed summarization when `OPENAI_API_KEY` is available
- Extractive fallback summarizer when the API is unavailable
- Validation that the output is actually shorter than the source
- Responsive UI with loading state, dark mode, and smooth motion
- Word counts for input and output
- `.txt` file upload from the browser or directly through `POST /summarize`
- Copy to clipboard
- Download summary as PDF
- Speech-to-text input in supported browsers
- Recent summary history stored in `localStorage`
- Health check endpoint at `GET /health`
- Lightweight unit tests for the API and summarization service

## Project Structure

```text
story_summaraization_project/
|-- app.py
|-- requirements.txt
|-- .env.example
|-- README.md
|-- samples/
|   |-- sample_input.txt
|   |-- sample_output.txt
|-- services/
|   |-- __init__.py
|   |-- extractive_summarizer.py
|   |-- openai_summarizer.py
|   |-- pdf_export.py
|   |-- summary_service.py
|   |-- text_utils.py
|-- static/
|   |-- script.js
|   |-- style.css
|-- templates/
|   |-- index.html
|-- tests/
|   |-- test_app.py
|   |-- test_summary_service.py
```

## Setup

1. Create and activate a virtual environment.

```powershell
python -m venv .venv
.venv\Scripts\activate
```

2. Install dependencies.

```powershell
pip install -r requirements.txt
```

3. Create a `.env` file from `.env.example`.

```powershell
Copy-Item .env.example .env
```

4. Add your OpenAI API key to `.env`.

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4.1-mini
```

5. Run the app.

```powershell
python app.py
```

6. Open the site in your browser.

```text
http://127.0.0.1:5000
```

7. Optional: run the test suite.

```powershell
python -m unittest discover -s tests
```

## API

### `POST /summarize`

JSON request:

```json
{
  "text": "Long input text goes here...",
  "length": "medium"
}
```

Multipart request:

- `text`: optional text field
- `file`: optional `.txt` upload
- `length`: `short`, `medium`, or `long`

Response:

```json
{
  "summary": "Shorter summary text...",
  "provider": "openai",
  "input_word_count": 220,
  "output_word_count": 94,
  "compression_ratio": 0.43
}
```

### `GET /health`

Response:

```json
{
  "status": "ok"
}
```

### `POST /download-summary`

Request:

```json
{
  "summary": "Shorter summary text...",
  "length": "medium"
}
```

Returns a downloadable PDF file.

## Sample Test Input

```text
Artificial intelligence is changing the way students learn. Schools are using AI tools to personalize lesson plans, identify learning gaps, and give faster feedback on assignments. Teachers can save time on repetitive tasks and focus more on mentoring students. At the same time, educators are concerned about overreliance on AI-generated answers, data privacy, and fairness in automated systems. To use AI responsibly, schools need clear policies, teacher training, and systems that keep human judgment at the center of decision-making.
```

## Sample Output

```text
Schools are using AI to personalize lessons, detect learning gaps, and speed up feedback, which helps teachers spend more time supporting students. However, concerns about privacy, fairness, and overreliance on generated answers mean schools need clear rules, training, and strong human oversight.
```

The sample files are included in [samples/sample_input.txt](/C:/Users/yaraa/OneDrive/Documents/story_summaraization_project/samples/sample_input.txt) and [samples/sample_output.txt](/C:/Users/yaraa/OneDrive/Documents/story_summaraization_project/samples/sample_output.txt).

## Notes

- If the OpenAI request fails or no API key is configured, the app falls back to an internal extractive summarizer.
- Speech input depends on browser support for the Web Speech API.
- Summary history is stored locally in the browser, not on the server.
- The backend rejects summaries that are not shorter than the original input.

## Update 1
This is the first update.

## Update 2
This is the second update.

## Update 3
This is the third update.

## Update 4
This is the fourth update.
