
import json
import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is missing from backend/.env"
    )

client = genai.Client(api_key=API_KEY)


def generate_tests_with_llm(source_code):
    prompt = f"""
You are a Python software testing assistant.

Analyze the code and suggest test cases.

Return only valid JSON with this structure:
{{
  "function_name": "function name",
  "analysis": "brief explanation",
  "tests": [
    {{
      "name": "test name",
      "input": {{"a": 2, "b": 3}},
      "expected": 5,
      "expect_error": false
    }}
  ]
}}

Include normal inputs, boundary cases, and edge cases.
Do not execute the submitted code.
Do not assume the current implementation is correct.
If intended behavior is unclear, state your assumption.

Submitted Python code:
{source_code}
"""

    try:
        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-3.6-flash"),
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "temperature": 0.2,
            },
        )

        result = json.loads(response.text)

        if not isinstance(result.get("tests"), list):
            raise ValueError("Invalid tests returned by Gemini.")

        if not isinstance(result.get("function_name"), str):
            raise ValueError("Function name missing from Gemini response.")

        return result

    except Exception as exc:
        raise ValueError(
            f"Gemini test generation failed: {exc}"
        ) from exc
