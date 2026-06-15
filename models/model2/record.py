import json
import queue
import csv
import os
import sys
from datetime import datetime
import sounddevice as sd
from vosk import Model, KaldiRecognizer

# Adds the root project directory to the path so config.py can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import CSV_FILE_PATH, CSV_COLUMNS, MODEL2_VOSK_PATH, SAMPLE_RATE, CHUNK_SIZE


# Audio queue — stores raw microphone chunks before Vosk processes them
audio_queue = queue.Queue()


def callback(indata, frames, time, status):
    """
    Triggered automatically by sounddevice for every audio chunk captured.
    Pushes raw bytes into the queue for Vosk to pick up and process.
    """
    if status:
        print(f"Audio warning: {status}")
    audio_queue.put(bytes(indata))


def load_model():
    """
    Loads the full 1.8GB Vosk model from the asr/ folder.
    This is significantly more accurate than the lgraph model
    but takes a few seconds to load due to its size.
    Exits cleanly with a helpful message if the model isn't found.

    Time complexity:  O(1)
    Space complexity: O(n) where n is the model size loaded into memory
    """
    if not os.path.exists(MODEL2_VOSK_PATH):
        print(f"Error: Vosk model not found at '{MODEL2_VOSK_PATH}'")
        print("Download from: https://alphacephei.com/vosk/models")
        sys.exit(1)

    print("Loading Vosk full model — this may take a moment...")
    model = Model(MODEL2_VOSK_PATH)
    recognizer = KaldiRecognizer(model, SAMPLE_RATE)
    print("Model loaded successfully.")
    return recognizer


def ensure_csv():
    """
    Creates the CSV file with the correct headers if it doesn't exist yet.
    Safe to call multiple times — won't overwrite existing data.

    Time complexity:  O(1)
    Space complexity: O(1)
    """
    os.makedirs(os.path.dirname(CSV_FILE_PATH), exist_ok=True)
    if not os.path.exists(CSV_FILE_PATH):
        with open(CSV_FILE_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
            writer.writeheader()


def save_row(name, raw_text, time_taken):
    """
    Appends one speaker turn as a new row in the CSV.
    Only fills in the columns we know at recording time —
    the enrichment columns get calculated later by enrich.py.

    Args:
        name (str):         speaker name entered before recording
        raw_text (str):     raw Vosk transcript — imperfect but unmodified
        time_taken (float): how long the sentence took in seconds

    Time complexity:  O(1)
    Space complexity: O(1)
    """
    row = {
        "timestamp": datetime.now().isoformat(),
        "name": name,
        "raw_text_vosk": raw_text,
        "text": "",            # filled by correct.py
        "time_taken_sec": round(time_taken, 2),
        "question_flag": "",   # filled by enrich.py
        "num_words": "",       # filled by enrich.py
        "text_size_chars": "", # filled by enrich.py
        "speech_rate_wps": "", # filled by enrich.py
        "speaker_turn_id": "", # filled by enrich.py
        "sentiment": "",       # filled by enrich.py
        "model_used": "model2",
        "accuracy_score": ""   # filled by enrich.py
    }

    with open(CSV_FILE_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writerow(row)

    print(f"Saved: [{name}] {raw_text}")


def record_turn(recognizer, name):
    """
    Records one speaker turn from the microphone using the full Vosk model.
    Streams audio in real time and waits until Vosk detects a complete sentence.
    Times the sentence automatically and saves the row to CSV.

    Args:
        recognizer: loaded Vosk KaldiRecognizer instance
        name (str): speaker name for this turn

    Time complexity:  O(n) where n is the number of audio chunks processed
    Space complexity: O(k) where k is CHUNK_SIZE in bytes
    """
    print(f"\n[{name}] Speak now... (press Ctrl+C when done)")

    start_time = datetime.now()

    try:
        with sd.RawInputStream(
            samplerate=SAMPLE_RATE,
            blocksize=CHUNK_SIZE,
            dtype="int16",
            channels=1,
            callback=callback,
        ):
            while True:
                data = audio_queue.get()

                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    text = result.get("text", "").strip()

                    if text:
                        time_taken = (datetime.now() - start_time).total_seconds()
                        print(f"Heard: {text}")
                        save_row(name, text, time_taken)
                        return text

    except KeyboardInterrupt:
        # Catch any final words Vosk hadn't finished processing
        final = json.loads(recognizer.FinalResult()).get("text", "").strip()
        if final:
            time_taken = (datetime.now() - start_time).total_seconds()
            save_row(name, final, time_taken)
        print("\nRecording stopped.")
        return None


def record_session():
    """
    Main recording loop for Model 2 — Vosk full + Claude.
    Asks for a speaker name before each turn and records one sentence at a time.
    Keeps going until the user types quit or chooses to stop.

    Time complexity:  O(n) where n is the number of recorded turns
    Space complexity: O(1) per turn — rows are written to disk immediately
    """
    print("\n=== Model 2: Vosk full + Claude ===")
    print("Recording meeting speech to CSV.\n")

    recognizer = load_model()
    ensure_csv()

    while True:
        name = input("\nEnter speaker name (or 'quit' to stop): ").strip()

        if name.lower() == "quit":
            print("\nRecording session ended.")
            break

        if not name:
            print("Name cannot be empty.")
            continue

        record_turn(recognizer, name)

        again = input("Record another turn? (y/n): ").strip().lower()
        if again != "y":
            print("\nRecording session ended.")
            break