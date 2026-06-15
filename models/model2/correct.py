import anthropic
import csv
import os
import sys

# Adds the root project directory to the path so config.py can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import CLAUDE_API_KEY, CLAUDE_MODEL, CLAUDE_MAX_TOKENS, CSV_FILE_PATH, CSV_COLUMNS


def correct_transcript(raw_text):
    """
    Sends a raw Vosk transcript to Claude for correction.
    Claude fixes spelling, punctuation and grammar without changing the meaning.
    This is the text normalisation step in the NLP pipeline.

    Args:
        raw_text (str): raw imperfect transcript from Vosk
        e.g. 'i think we shold fokus on soshal media'

    Returns:
        str: corrected transcript from Claude
        e.g. 'I think we should focus on social media.'

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
    Only processes rows where the text column is empty — skips already corrected rows.

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
        # Only correct rows that haven't been corrected yet
        if not row.get("text", "").strip():
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