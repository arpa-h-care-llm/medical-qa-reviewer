<--
This source file is part of the ARPA-H CARE LLM project

SPDX-FileCopyrightText: 2025 Stanford University and the project authors (see AUTHORS.md)

SPDX-License-Identifier: MIT

-->

# Discharge Summary QA Viewer

This is a Streamlit-based application for reviewing and editing LLM-generated responses to discharge summary questions. It supports two usage modes:

1. **Pre-generated Responses Mode** — Upload an Excel file with LLM-generated responses already included.
2. **Prompt-to-LLM Mode** — Upload an Excel file with only prompts, and the app will generate responses using a placeholder LLM function (which you can replace with a real model call).

---

## Input File Formats

Depending on your selected mode, the Excel file should follow one of these formats:

### Mode 1: Includes LLM-generated Response
| Note Id | Discharge Summary | Question | LLM-generated Response |
|---------|--------------------|----------|-------------------------|

### Mode 2: Needs LLM to generate Response
| Note Id | Discharge Summary | Question | Prompt |
|---------|--------------------|----------|--------|

> ⚠️ When using Mode 2, the app ignores any existing `LLM-generated Response` column and generates new responses using a placeholder function.

---

## How to Run

### Prerequisites

- Python 3.8+
- Dependencies listed in `requirements.txt`

### Installation

```bash
git clone https://github.com/YOUR_USERNAME/discharge-summary-qa-viewer.git
cd discharge-summary-qa-viewer
pip install -r requirements.txt
```

### Start the App
```bash
streamlit run qa_expert_reviewer_app.py
```

![App Screenshot](docs/demo_img/.png)

### About the LLM Integration

The app includes a function called generate_llm_response_from_prompt() as a placeholder.
```python
def generate_llm_response_from_prompt(prompt, discharge_summary, question):
    """
    Placeholder for real LLM API call. Replace this with OpenAI, Vertex AI, Claude, etc.
    """
    return "Generated response based on your prompt and summary..."
```

To connect it to a real LLM (like OpenAI's GPT-4 or Google's Gemini), replace this function with the actual API call and handle authentication.


### Disclaimer

This app is for local use and prototyping only. Do not upload sensitive or identifiable patient data unless deployed in a secure, compliant environment.


### License

MIT License