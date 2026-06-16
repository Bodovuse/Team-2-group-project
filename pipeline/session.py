import csv
import os
import sys
import select
from datetime import datetime

# Adds root directory to path so all modules can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CSV_COLUMNS, LIVE_RECORDINGS_PATH
from pipeline.correct import correct_transcript
from pipeline.enrich import enrich_csv
from pipeline.validate import validate_csv


def generate_session_filename(session_name):
    """
    Generates a unique filename for the recording session.
    Combines the user's chosen name with a timestamp to guarantee uniqueness.
    Spaces are converted to hyphens and the name is lowercased for clean filenames.

    Format: meeting-{name}-{YYYYMMDD}-{HHMM}.csv
    Example: meeting-bda-project-20260614-0930.csv

    Args:
        session_name (str): name chosen by the user at session start

    Returns:
        str: full file path for the session CSV

    Time complexity:  O(1)
    Space complexity: O(1)
    """
    clean_name = session_name.strip().lower().replace(" ", "-")
    timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    filename = f"meeting-{clean_name}-{timestamp}.csv"
    os.makedirs(LIVE_RECORDINGS_PATH, exist_ok=True)
    return os.path.join(LIVE_RECORDINGS_PATH, filename)


def initialise_csv(csv_path):
    """
    Creates the session CSV file with the correct headers.
    Called once at the start of each recording session.
    Each session gets its own file so there is no risk of
    mixing data from different sessions.

    Args:
        csv_path (str): full file path for the session CSV

    Time complexity:  O(1)
    Space complexity: O(1)
    """
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()


def save_row(csv_path, name, raw_text, corrected_text, time_taken, model_used):
    """
    Appends one completed speaker turn as a new row in the session CSV.
    Both the raw ASR transcript and the corrected LLM version are saved
    so the accuracy score can be calculated later during enrichment.
    Enrichment columns are left empty here — enrich.py fills them in
    after the session ends.

    Args:
        csv_path (str):       full path to the session CSV file
        name (str):           speaker name for this turn
        raw_text (str):       raw transcript from the ASR model
        corrected_text (str): corrected transcript from Claude
        time_taken (float):   how long the sentence took in seconds
        model_used (str):     which model produced this row

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
        "model_used": model_used,
        "accuracy_score": ""   # filled by enrich.py
    }

    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writerow(row)


def register_speakers():
    """
    Registers all speakers at the start of the session.
    Asks how many speakers are present then collects each name.
    Returns a list of speaker names in the order they were entered.
    The session cycles through this list when s is pressed to switch speaker.

    Returns:
        list: speaker names in registration order

    Time complexity:  O(k) where k is the number of speakers
    Space complexity: O(k) for storing the speaker list
    """
    print("\n" + "=" * 55)
    print("  REGISTER SPEAKERS")
    print("=" * 55)

    while True:
        try:
            count = int(input("\nHow many speakers are in this meeting? ").strip())
            if count > 0:
                break
            print("Please enter a number greater than 0.")
        except ValueError:
            print("Please enter a valid number.")

    speakers = []
    for i in range(1, count + 1):
        name = input(f"  Speaker {i} name: ").strip()
        while not name:
            print("  Name cannot be empty.")
            name = input(f"  Speaker {i} name: ").strip()
        speakers.append(name)

    print(f"\nSpeakers registered: {', '.join(speakers)}")
    return speakers


def get_row_count(csv_path):
    """
    Counts how many data rows are in the session CSV.
    Used at the end of the session to show a summary.
    Excludes the header row from the count.

    Args:
        csv_path (str): full path to the session CSV file

    Returns:
        int: number of data rows in the CSV

    Time complexity:  O(n) where n is the number of rows
    Space complexity: O(1)
    """
    if not os.path.exists(csv_path):
        return 0
    with open(csv_path, newline="", encoding="utf-8") as f:
        return sum(1 for row in csv.DictReader(f))


def check_for_command():
    """
    Checks if the user has typed a command without blocking the recording.
    Uses select() to check if there is input waiting on stdin.
    If nothing is typed within 0.1 seconds recording continues automatically.

    This is what makes the recording feel continuous — the mic keeps listening
    and the user can type a command at any point between sentences.

    Commands:
        s — switch to next speaker
        q — end the session

    Returns:
        str or None: 's', 'q', or None if nothing was typed

    Time complexity:  O(1)
    Space complexity: O(1)
    """
    # select() checks if stdin has data ready to read without blocking
    # timeout of 0.1 seconds — if nothing typed, returns immediately
    if select.select([sys.stdin], [], [], 0.1)[0]:
        cmd = sys.stdin.readline().strip().lower()
        if cmd in ("s", "q"):
            return cmd
    return None


def run_session(model_choice, adapter, model_used):
    """
    The main live recording session for the Meeting Speech Analytics Pipeline.

    This is the core of the product — the user speaks, the ASR model transcribes,
    Claude corrects, and the result is shown on screen and saved to CSV in real time.

    The session runs as a continuous loop — the microphone stays open and keeps
    listening after every sentence. The user can type commands between sentences:
        s + Enter — switch to the next speaker in the registered list
        q + Enter — end the session cleanly

    After the session ends enrichment and validation run automatically
    on the live session CSV — not the synthetic dataset.

    The session flow:
        1. User names the session — filename generated with timestamp
        2. Speakers registered — names stored in order
        3. Model loads once
        4. Mic opens — keeps listening continuously
        5. Each sentence transcribed → corrected → shown → saved
        6. User types s to switch speaker or q to quit between sentences
        7. Enrichment and validation run automatically at the end

    Args:
        model_choice (int): 1, 2 or 3 — used for display purposes
        adapter (module):   the loaded model adapter — exposes load() and transcribe()
        model_used (str):   string label saved to CSV — 'model1', 'model2' or 'model3'

    Time complexity:  O(n) where n is the number of recorded turns
    Space complexity: O(1) per turn — rows written to disk immediately
    """

    # ── Session setup ──────────────────────────────────────────
    print("\n" + "=" * 55)
    print("  NEW RECORDING SESSION")
    print("=" * 55)

    session_name = input("\nGive this session a name: ").strip()
    while not session_name:
        print("Session name cannot be empty.")
        session_name = input("Give this session a name: ").strip()

    csv_path = generate_session_filename(session_name)
    initialise_csv(csv_path)

    print(f"\nSession file: {os.path.basename(csv_path)}")
    print(f"Saved to:     {csv_path}")

    # ── Speaker registration ───────────────────────────────────
    speakers = register_speakers()
    speaker_index = 0

    # ── Load the ASR model ─────────────────────────────────────
    recognizer = adapter.load()

    # ── Recording loop ─────────────────────────────────────────
    print("\n" + "=" * 55)
    print("  RECORDING IN PROGRESS")
    print("=" * 55)
    print(f"\nCurrent speaker: {speakers[speaker_index]}")
    print("Type 's' + Enter to switch speaker, 'q' + Enter to end session.\n")

    stop = False

    while not stop:
        print(f"🎙  Listening... [{speakers[speaker_index]}]")

        try:
            # Transcribe one sentence — blocks until speech detected
            raw_text, time_taken = adapter.transcribe(recognizer)

        except KeyboardInterrupt:
            stop = True
            break

        if raw_text:
            # Show raw transcript so user can see what ASR heard
            print(f"\n  Raw:        {raw_text}")

            # Correct immediately with Claude
            corrected_text = correct_transcript(raw_text)

            # Show corrected version for direct comparison
            print(f"  Corrected:  {corrected_text}")
            print(f"  Speaker:    {speakers[speaker_index]}")
            print(f"  Time:       {round(time_taken, 2)}s")

            # Save to the live session CSV
            save_row(
                csv_path,
                speakers[speaker_index],
                raw_text,
                corrected_text,
                time_taken,
                model_used
            )
            print(f"  Saved to CSV ✓\n")

        # Check for s or q command typed between sentences
        cmd = check_for_command()
        if cmd == "q":
            stop = True
        elif cmd == "s":
            speaker_index = (speaker_index + 1) % len(speakers)
            print(f"Switched to: {speakers[speaker_index]}\n")

    # ── Session summary ────────────────────────────────────────
    print("\n" + "=" * 55)
    print("  SESSION ENDED")
    print("=" * 55)

    row_count = get_row_count(csv_path)
    print(f"\n  Session:  {os.path.basename(csv_path)}")
    print(f"  Rows:     {row_count}")
    print(f"  Speakers: {', '.join(speakers)}")

    # ── Run enrichment and validation on the live session CSV ──
    # config.CSV_FILE_PATH is updated to point to the live session file
    # so enrichment and validation run on the correct data
    import config
    config.CSV_FILE_PATH = csv_path

    print(f"\nRunning enrichment...")
    enrich_csv()

    print("\nRunning validation...")
    passed = validate_csv()

    if passed:
        print("\nPipeline complete — dataset is ready for analytics.")
    else:
        print("\nPipeline complete — validation found issues.")
        print("Fix the issues above before running analytics.")

    return csv_path