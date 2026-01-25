import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY not set")

genai.configure(api_key=API_KEY)

# Gemini 2 Flash (free tier)
MODEL_NAME = "models/gemini-2.5-flash"


def gemini_llm(prompt: str) -> str:
    model = genai.GenerativeModel(
        MODEL_NAME,
        generation_config={
            "temperature": 0,
            "max_output_tokens": 256
        }
    )

    response = model.generate_content(prompt)

    if not response.text:
        raise ValueError("Empty response from Gemini")

    return response.text.strip()
