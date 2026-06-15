import anthropic
import csv
import os
import sys

# Adds the root project directory to the path so config.py can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import CLAUDE_API_KEY, CLAUDE_MODEL, CLAUDE_MAX_TOKENS, CSV_FILE_PATH, CSV_COLUMNS


def correct_transcript(raw_text):
    """
    Sends a raw Faster-Whisper transcript to Claude for correction.
    Whisper is already more accurate than Vosk so fewer corrections
    are expected — but Claude still fixes any remaining issues.

    Args:
        raw_text (str): raw transcript from Faster-Whisper

    Returns:
        str: corrected transcript from Claude

    Time complexity:  O(n) where n is the length of the input text
    Space complexity: O(n) for storing the corrected output
    """
    client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=CLAUDE_MAX_TOKENS,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Correct the spelling, punctuation and grammar of this transcript. "
                    f"Do not change the meaning. "
                    f"Return only the corrected sentence and nothing else: {raw_text}"
                )
            }
        ]
    )

    return message.content[0].text.strip()


def correct_csv():
    """
    Reads the CSV and sends each raw_text_vosk value to Claude for correction.
    Writes the corrected text back to the text column.
    Only processes rows where model_used is model3 and text is empty —
    avoids reprocessing rows from other models.

    Time complexity:  O(n) where n is the number of rows to correct
    Space complexity: O(n) to store all rows in memory
    """
    if not os.path.exists(CSV_FILE_PATH):
        print(f"Error: CSV file not found at '{CSV_FILE_PATH}'")
        return

    rows = []
    with open(CSV_FILE_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    corrected = 0

    for row in rows:
        # Only correct model3 rows that haven't been corrected yet
        if row.get("model_used") == "model3" and not row.get("text", "").strip():
            raw = row["raw_text_vosk"].strip()
            if raw:
                print(f"Correcting: {raw}")
                row["text"] = correct_transcript(raw)
                corrected += 1

    # Write corrected rows back to CSV
    with open(CSV_FILE_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nCorrection complete — {corrected} rows corrected.")


if __name__ == "__main__":
    correct_csv()