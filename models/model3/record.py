import csv
import os
import sys
import tempfile
from datetime import datetime
import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel

# Adds the root project directory to the path so config.py can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import (
    CSV_FILE_PATH, CSV_COLUMNS, MODEL3_WHISPER_SIZE,
    MODEL3_WHISPER_DEVICE, MODEL3_WHISPER_COMPUTE,
    SAMPLE_RATE, CHUNK_SIZE
)


def load_model():
    """
    Loads the Faster-Whisper large-v3 model.
    Downloads automatically on first run and caches locally.
    Set to run on CPU with int8 compute for cross-platform compatibility.

    Time complexity:  O(1) after initial download
    Space complexity: O(n) where n is the model size loaded into memory
    """
    print("Loading Faster-Whisper model — this may take a moment...")
    model = WhisperModel(
        MODEL3_WHISPER_SIZE,
        device=MODEL3_WHISPER_DEVICE,
        compute_type=MODEL3_WHISPER_COMPUTE
    )
    print("Model loaded successfully.")
    return model


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
    Only fills in the columns known at recording time —
    enrichment columns are calculated later by enrich.py.

    Args:
        name (str):         speaker name entered before recording
        raw_text (str):     raw Whisper transcript
        time_taken (float): how long the recording took in seconds

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
        "model_used": "model3",
        "accuracy_score": ""   # filled by enrich.py
    }

    with open(CSV_FILE_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writerow(row)

    print(f"Saved: [{name}] {raw_text}")


def record_audio(duration=10):
    """
    Records audio from the microphone for a set duration.
    Unlike Vosk, Faster-Whisper processes complete audio files
    rather than streaming in real time.

    Args:
        duration (int): how many seconds to record — default is 10

    Returns:
        numpy array of recorded audio samples

    Time complexity:  O(n) where n is the duration in seconds
    Space complexity: O(n) for storing the audio samples
    """
    print(f"Recording for {duration} seconds... speak now!")
    audio = sd.rec(
        int(duration * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32"
    )
    sd.wait()
    print("Recording complete.")
    return audio.flatten()


def transcribe_audio(model, audio):
    """
    Transcribes recorded audio using Faster-Whisper.
    Joins all detected segments into a single transcript string.

    Args:
        model: loaded WhisperModel instance
        audio: numpy array of audio samples

    Returns:
        str: full transcript of the recording

    Time complexity:  O(n log n) for Whisper inference
    Space complexity: O(n) where n is the audio duration
    """
    # Save audio to a temporary wav file for Whisper to process
    import wave
    import struct

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp_path = tmp.name

    with wave.open(tmp_path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        audio_int16 = (audio * 32767).astype(np.int16)
        wf.writeframes(audio_int16.tobytes())

    segments, _ = model.transcribe(tmp_path, language="en")
    transcript = " ".join(segment.text.strip() for segment in segments)

    os.unlink(tmp_path)
    return transcript.strip()


def record_turn(model, name):
    """
    Records one speaker turn and transcribes it using Faster-Whisper.
    Asks the user how long to record before starting.

    Args:
        model: loaded WhisperModel instance
        name (str): speaker name for this turn

    Time complexity:  O(n) where n is the recording duration
    Space complexity: O(n) for storing the audio
    """
    try:
        duration = int(input(f"\n[{name}] How many seconds to record? (default 10): ").strip() or "10")
    except ValueError:
        duration = 10

    start_time = datetime.now()
    audio = record_audio(duration)
    time_taken = (datetime.now() - start_time).total_seconds()

    print("Transcribing...")
    text = transcribe_audio(model, audio)

    if text:
        print(f"Heard: {text}")
        save_row(name, text, time_taken)
        return text
    else:
        print("Nothing detected — please try again.")
        return None


def record_session():
    """
    Main recording loop for Model 3 — Faster-Whisper + Claude.
    Asks for a speaker name then records one sentence at a time.
    Keeps going until the user types quit or chooses to stop.

    Time complexity:  O(n) where n is the number of recorded turns
    Space complexity: O(1) per turn — rows written to disk immediately
    """
    print("\n=== Model 3: Faster-Whisper + Claude ===")
    print("Recording meeting speech to CSV.\n")

    model = load_model()
    ensure_csv()

    while True:
        name = input("\nEnter speaker name (or 'quit' to stop): ").strip()

        if name.lower() == "quit":
            print("\nRecording session ended.")
            break

        if not name:
            print("Name cannot be empty.")
            continue

        record_turn(model, name)

        again = input("Record another turn? (y/n): ").strip().lower()
        if again != "y":
            print("\nRecording session ended.")
            break