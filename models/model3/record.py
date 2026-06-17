import csv
import os
import sys
import wave
import tempfile
from datetime import datetime
import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel

# Adds the root project directory to the path so config.py can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import (
    CSV_COLUMNS, MODEL3_WHISPER_SIZE,
    MODEL3_WHISPER_DEVICE, MODEL3_WHISPER_COMPUTE,
    SAMPLE_RATE, LIVE_CSV_MODEL3
)

# Import Claude correction so it runs immediately after each transcription
# Unlike Vosk, Whisper processes a complete audio file before returning text
# so correction still happens right after transcription — just not mid stream
from models.model3.correct import correct_transcript


def load_model():
    """
    Loads the Faster-Whisper large-v3 model.
    Downloads automatically on first run from HuggingFace and caches locally —
    so subsequent runs load much faster.
    Set to run on CPU with int8 compute type for cross-platform compatibility.
    No GPU required — works on any machine.

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


def initialise_csv(new_session):
    """
    Prepares the live CSV file before the recording session starts.
    Two modes:
        New session   — wipes the file and writes fresh headers
                        so old data from previous sessions doesn't interfere
        Continue      — leaves existing data intact and appends new rows
                        useful if the session was interrupted mid way

    Args:
        new_session (bool): True to wipe and start fresh, False to append

    Time complexity:  O(1)
    Space complexity: O(1)
    """
    os.makedirs(os.path.dirname(LIVE_CSV_MODEL3), exist_ok=True)

    if new_session:
        with open(LIVE_CSV_MODEL3, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
            writer.writeheader()
        print("New session started — live CSV cleared and ready.")
    else:
        if not os.path.exists(LIVE_CSV_MODEL3):
            with open(LIVE_CSV_MODEL3, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
                writer.writeheader()
        print("Continuing existing session — new rows will be appended.")


def save_row(name, raw_text, corrected_text, time_taken):
    """
    Appends one completed speaker turn as a new row in the live CSV.
    Both the raw Whisper transcript and Claude corrected version are saved
    so the accuracy score can be calculated later during enrichment.
    Enrichment columns are left empty — enrich.py fills them in.

    Args:
        name (str):           speaker name entered before recording
        raw_text (str):       raw transcript from Faster-Whisper
        corrected_text (str): corrected transcript from Claude
        time_taken (float):   how long the recording took in seconds

    Time complexity:  O(1)
    Space complexity: O(1)
    """
    row = {
        "timestamp": datetime.now().isoformat(),
        "name": name,
        "raw_text_vosk": raw_text,
        "text": corrected_text,
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

    with open(LIVE_CSV_MODEL3, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writerow(row)


def record_audio(duration):
    """
    Records audio from the microphone for a fixed duration.
    Unlike Vosk which streams in real time, Faster-Whisper needs a complete
    audio file to process — so we record the full sentence first then transcribe.
    Returns a numpy array of audio samples ready for Whisper to process.

    Args:
        duration (int): how many seconds to record

    Returns:
        numpy array of recorded audio samples

    Time complexity:  O(n) where n is the duration in seconds
    Space complexity: O(n) for storing the audio samples in memory
    """
    print(f"  Recording for {duration} seconds — speak now!")
    audio = sd.rec(
        int(duration * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32"
    )
    sd.wait()
    print("  Recording complete — transcribing...")
    return audio.flatten()


def transcribe_audio(model, audio):
    """
    Transcribes a recorded audio array using Faster-Whisper.
    Saves the audio to a temporary wav file first because Whisper
    requires a file path rather than raw audio data.
    Joins all detected segments into one complete transcript string.
    The temporary file is deleted immediately after transcription.

    Args:
        model: loaded WhisperModel instance
        audio: numpy array of audio samples from record_audio()

    Returns:
        str: full transcript of the recorded audio

    Time complexity:  O(n log n) for Whisper inference
    Space complexity: O(n) where n is the audio duration
    """
    # Save audio to a temporary wav file for Whisper to process
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

    # Clean up the temporary file straight away
    os.unlink(tmp_path)
    return transcript.strip()


def record_turn(model, name):
    """
    Records one speaker turn and transcribes it using Faster-Whisper.
    After transcription Claude corrects the text immediately —
    both are shown on screen so the user can see the difference.
    The key difference from model2 is that Whisper records a fixed
    duration rather than streaming — the user decides how long to record.

    Args:
        model: loaded WhisperModel instance
        name (str): speaker name for this turn

    Time complexity:  O(n) where n is the recording duration
    Space complexity: O(n) for storing the audio before transcription
    """
    print(f"\n[{name}]\n")

    try:
        duration = int(input("  How many seconds to record? (default 10): ").strip() or "10")
    except ValueError:
        duration = 10

    start_time = datetime.now()
    audio = record_audio(duration)
    time_taken = (datetime.now() - start_time).total_seconds()

    raw_text = transcribe_audio(model, audio)

    if raw_text:
        # Show raw Whisper transcript so the user can see what it heard
        print(f"  Raw (Whisper):      {raw_text}")

        # Immediately send to Claude for correction
        print(f"  Correcting with Claude...")
        corrected_text = correct_transcript(raw_text)

        # Show corrected version below so the user can compare
        print(f"  Corrected (Claude): {corrected_text}")
        print(f"  Time taken:         {round(time_taken, 2)}s")

        # Save both to the live CSV
        save_row(name, raw_text, corrected_text, time_taken)
        print(f"  Saved to CSV ✓\n")

        return raw_text, corrected_text
    else:
        print("  Nothing detected — please try again.")
        return None, None


def record_session(new_session=True):
    """
    Main live recording loop for Model 3 — Faster-Whisper + Claude.
    Loads the model once then loops — asking for a speaker name
    and recording one turn at a time until the user stops.
    Each recording is transcribed by Whisper then corrected by Claude
    before the next speaker takes their turn.

    Args:
        new_session (bool): True to wipe CSV and start fresh, False to append

    Time complexity:  O(n) where n is the number of recorded turns
    Space complexity: O(1) per turn — rows written to disk immediately
    """
    print("\n=== Model 3: Faster-Whisper + Claude ===")
    print("Speak naturally — Whisper transcribes and Claude corrects after each turn.\n")

    model = load_model()
    initialise_csv(new_session)

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
        