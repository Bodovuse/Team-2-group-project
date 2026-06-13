"""Simple Gemini example.

Enter a prompt, send it to Gemini, and print the output.

Set GEMINI_API_KEY before running:
    export GEMINI_API_KEY="your_key_here"
"""

import os

from google import genai


MODEL_NAME = "gemini-2.5-flash"


def ask_gemini(prompt):
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
    return response.text


if __name__ == "__main__":
    prompt = (
        "Correct this transcript. Return only the corrected sentence:\n"
        "helo team today we discuss mobile app growth"
    )

    output = ask_gemini(prompt)
    print(output)
