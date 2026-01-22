import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY not set")

genai.configure(api_key=API_KEY)

MODEL_NAME = "models/gemini-1.5-flash-001"  # ✅ correct SDK model id

def gemini_llm(prompt: str) -> dict:
    model = genai.GenerativeModel(
        MODEL_NAME,
        generation_config={
            "temperature": 0,
            "top_p": 1,
            "max_output_tokens": 512
        }
    )

    response = model.generate_content(prompt)
    text = response.text.strip()

    # Strip markdown fences if present
    if text.startswith("```"):
        text = text.strip("`").replace("json", "", 1).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        raise ValueError(f"Gemini returned non-JSON:\n{text}")
