import os
import sys

# Adds root directory to path so all modules can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pipeline.enrich import enrich_csv
from pipeline.validate import validate_csv


def select_model():
    """
    Asks the user which model to use for recording.
    Returns the model number as an integer.
    """
    print("\n" + "=" * 55)
    print("  MEETING SPEECH ANALYTICS PIPELINE")
    print("=" * 55)
    print("\nWhich model would you like to use?\n")
    print("  1 — Vosk lgraph + Ollama   (fast, offline, less accurate)")
    print("  2 — Vosk full + Claude     (accurate, requires internet)")
    print("  3 — Faster-Whisper + Claude (most accurate, requires internet)")
    print()

    while True:
        choice = input("Enter choice (1, 2 or 3): ").strip()
        if choice in {"1", "2", "3"}:
            return int(choice)
        print("Please enter 1, 2 or 3.")


def select_mode():
    """
    Asks whether to record new data or run the pipeline on existing CSV data.
    """
    print("\nWhat would you like to do?\n")
    print("  1 — Record new meeting speech")
    print("  2 — Run pipeline on existing CSV data")
    print()

    while True:
        choice = input("Enter choice (1 or 2): ").strip()
        if choice in {"1", "2"}:
            return int(choice)
        print("Please enter 1 or 2.")


def run_recording(model_choice):
    """
    Runs the recording stage for the chosen model.
    Each model uses a different ASR approach —
    model1 uses Vosk lgraph, model2 uses Vosk full, model3 uses Faster-Whisper.
    """
    if model_choice == 1:
        from models.model1.voskLib import voskMain
        voskMain()
    elif model_choice == 2:
        from models.model2.record import record_session
        record_session()
    elif model_choice == 3:
        from models.model3.record import record_session
        record_session()


def run_correction(model_choice):
    """
    Runs the AI correction stage for the chosen model.
    Model 1 correction is handled by Ollama inside voskLib.
    Models 2 and 3 use Claude API for correction.
    """
    if model_choice == 1:
        print("\nModel 1 uses Ollama for correction — make sure Ollama is running.")
    elif model_choice == 2:
        from models.model2.correct import correct_csv
        print("\nRunning Claude correction for model 2...")
        correct_csv()
    elif model_choice == 3:
        from models.model3.correct import correct_csv
        print("\nRunning Claude correction for model 3...")
        correct_csv()


def main():
    """
    Central controller for the Meeting Speech Analytics Pipeline.

    Runs the pipeline in order:
        Stage 1 — Record speech using the chosen ASR model
        Stage 2 — Correct transcript using the chosen LLM
        Stage 3 — Enrich CSV with calculated columns
        Stage 4 — Validate CSV is correct before analytics
        Stage 5 — Analytics handled separately
    """
    model_choice = select_model()
    mode_choice = select_mode()

    if mode_choice == 1:
        print(f"\nStarting recording with model {model_choice}...")
        run_recording(model_choice)
        run_correction(model_choice)

    print("\nRunning enrichment...")
    enrich_csv()

    print("\nRunning validation...")
    passed = validate_csv()

    if passed:
        print("\nPipeline complete — dataset is ready for analytics.")
        print("Run pipeline/analytics.py to generate charts and stats.")
    else:
        print("\nPipeline complete — validation found issues, fix before running analytics.")


if __name__ == "__main__":
    main()