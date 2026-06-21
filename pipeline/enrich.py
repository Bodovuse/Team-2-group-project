import csv
import os
import sys
from textblob import TextBlob
from difflib import SequenceMatcher

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from config import CSV_COLUMNS


def calculate_question_flag(text):
    # True if the corrected sentence ends with a question mark
    return text.strip().endswith("?")


def calculate_num_words(text):
    # Count the number of words in the corrected text
    return len(text.strip().split())


def calculate_text_size_chars(text):
    # Count the number of characters in the corrected text
    return len(text.strip())


def calculate_speech_rate(num_words, time_taken_sec):
    # Words per second — how fast the speaker was talking
    # Rounded to 2 decimal places for readability
    if float(time_taken_sec) == 0:
        return 0.0
    return round(num_words / float(time_taken_sec), 2)


def calculate_sentiment(text):
    # Uses TextBlob to analyse the polarity of the sentence
    # Polarity > 0 = positive, < 0 = negative, 0 = neutral
    polarity = TextBlob(text).sentiment.polarity
    if polarity > 0:
        return "positive"
    elif polarity < 0:
        return "negative"
    else:
        return "neutral"


def calculate_accuracy_score(raw_text, corrected_text):
    # Compares raw ASR output to corrected LLM output
    # Uses SequenceMatcher to produce a similarity ratio between 0 and 1
    # 1.0 = identical, 0.0 = completely different
    return round(
        SequenceMatcher(None, raw_text.lower(), corrected_text.lower()).ratio(), 2
    )


def calculate_speaker_turn_id(rows):
    # Assigns a running turn count per speaker
    # First time a speaker speaks = 1, second time = 2 etc
    speaker_counts = {}
    for row in rows:
        name = row["name"]
        model = row["model_used"]
        # Only count turns for model2 to avoid triple counting
        # since all three models record the same sentence
        if model == "model2":
            speaker_counts[name] = speaker_counts.get(name, 0) + 1
        row["speaker_turn_id"] = speaker_counts.get(name, 1)
    return rows


def enrich_csv():
    """
    Stage 3 — Enrich the dataset

    Reads the CSV file and calculates all derived columns using
    Python logic only — no AI involved at this stage.

    Reads from config.CSV_FILE_PATH dynamically so it always points
    to the correct file — whether synthetic or live session data.

    Columns calculated:
        question_flag    — True if text ends with ?
        num_words        — word count of corrected text
        text_size_chars  — character count of corrected text
        speech_rate_wps  — words per second
        sentiment        — positive, negative or neutral
        accuracy_score   — similarity between raw and corrected text
        speaker_turn_id  — running turn count per speaker

    Time complexity:  O(n) where n is the number of rows
    Space complexity: O(n) to store all rows in memory
    """
    if not os.path.exists(config.CSV_FILE_PATH):
        print(f"Error: CSV file not found at '{config.CSV_FILE_PATH}'")
        return

    rows = []
    with open(config.CSV_FILE_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    if not rows:
        print("Error: CSV file is empty.")
        return

    # Calculate all enrichment columns for each row
    for row in rows:
        text = row.get("text", "").strip()
        raw_text = row.get("raw_text_vosk", "").strip()
        time_taken = row.get("time_taken_sec", "0")

        row["question_flag"] = calculate_question_flag(text)
        row["num_words"] = calculate_num_words(text)
        row["text_size_chars"] = calculate_text_size_chars(text)
        row["speech_rate_wps"] = calculate_speech_rate(
            row["num_words"], time_taken
        )
        row["sentiment"] = calculate_sentiment(text)
        row["accuracy_score"] = calculate_accuracy_score(raw_text, text)

    # Calculate speaker turn IDs separately
    rows = calculate_speaker_turn_id(rows)

    # Write enriched rows back to CSV
    with open(config.CSV_FILE_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Enrichment complete — {len(rows)} rows processed.")


if __name__ == "__main__":
    enrich_csv()