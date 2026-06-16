import os
import sys

# Adds root directory to path so all modules can be imported from anywhere
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def select_model():
    """
    Presents the three available models to the user and asks them to choose.
    Each model uses a different combination of ASR and LLM technology —
    giving the user the ability to compare transcription accuracy and speed
    across different approaches.

    Model 1 is fully offline using Vosk lgraph and Ollama locally.
    Model 2 uses the full Vosk model with Claude API for better accuracy.
    Model 3 uses Faster-Whisper which is the most accurate but not live streaming.

    Returns:
        tuple: (model_choice, adapter, model_used)
               model_choice — int 1, 2 or 3
               adapter      — the loaded adapter module for the chosen model
               model_used   — string label for the CSV column

    Time complexity:  O(1)
    Space complexity: O(1)
    """
    print("\nWhich model would you like to use?\n")
    print("  1 — Vosk lgraph + Ollama    (fast, offline, less accurate)")
    print("  2 — Vosk full + Claude      (accurate, requires internet)")
    print("  3 — Faster-Whisper + Claude (most accurate, requires internet)")
    print()

    while True:
        choice = input("Enter choice (1, 2 or 3): ").strip()
        if choice == "1":
            from models.model1 import adapter
            return 1, adapter, "model1"
        elif choice == "2":
            from models.model2 import adapter
            return 2, adapter, "model2"
        elif choice == "3":
            from models.model3 import adapter
            return 3, adapter, "model3"
        print("Please enter 1, 2 or 3.")


def select_analytics_dataset():
    """
    Asks the user which dataset to run analytics on.
    Shows both synthetic datasets and live recording sessions.
    Returns the file path of the chosen dataset.

    Returns:
        str: full file path of the chosen CSV dataset

    Time complexity:  O(n) where n is the number of live sessions
    Space complexity: O(n) for storing session list
    """
    from config import CSV_FILE_PATH, LIVE_RECORDINGS_PATH
    from pipeline.manage import get_all_sessions

    print("\nWhich dataset would you like to run analytics on?\n")
    print("  1 — Synthetic formal meeting (meetings1-formal.csv)")

    sessions = get_all_sessions()
    for i, session in enumerate(sessions, 2):
        print(f"  {i} — {session['filename']} ({session['rows']} rows, {session['date']})")

    print()

    options = {"1": CSV_FILE_PATH}
    for i, session in enumerate(sessions, 2):
        options[str(i)] = session["path"]

    while True:
        choice = input(f"Enter choice (1-{len(options)}): ").strip()
        if choice in options:
            return options[choice]
        print(f"Please enter a number between 1 and {len(options)}.")


def main():
    """
    Central controller for the Meeting Speech Analytics Pipeline.

    This is the entry point for the entire project.
    It presents the main menu and routes the user to the correct feature.

    Menu options:
        1 — Start a new recording session
            Guides the user through model selection, speaker registration
            and live recording. Correction, enrichment and validation
            run automatically after the session ends.

        2 — Manage existing recordings
            View summaries, delete or rename session files.

        3 — Run analytics on a dataset
            Choose a synthetic or live dataset and run the full
            analytics report with charts.

        4 — Exit

    Time complexity:  O(1) for menu navigation
    Space complexity: O(1)
    """
    while True:
        print("\n" + "=" * 55)
        print("  MEETING SPEECH ANALYTICS PIPELINE")
        print("=" * 55)
        print("\nWhat would you like to do?\n")
        print("  1 — Start a new recording session")
        print("  2 — Manage existing recordings")
        print("  3 — Run analytics on a dataset")
        print("  4 — Exit")
        print()

        choice = input("Enter choice: ").strip()

        if choice == "1":
            # Start a new live recording session
            model_choice, adapter, model_used = select_model()
            from pipeline.session import run_session
            run_session(model_choice, adapter, model_used)

        elif choice == "2":
            # Manage existing recording sessions
            from pipeline.manage import manage_recordings
            manage_recordings()

        elif choice == "3":
            # Run analytics on a chosen dataset
            csv_path = select_analytics_dataset()
            import config
            config.CSV_FILE_PATH = csv_path

            from pipeline.enrich import enrich_csv
            from pipeline.validate import validate_csv
            from pipeline.analytics import run_analytics

            print(f"\nRunning enrichment on {os.path.basename(csv_path)}...")
            enrich_csv()

            print("\nRunning validation...")
            passed = validate_csv()

            if passed:
                print("\nRunning analytics...")
                run_analytics()
            else:
                print("\nFix validation issues before running analytics.")

        elif choice == "4":
            print("\nGoodbye!")
            break

        else:
            print("Please enter 1, 2, 3 or 4.")


if __name__ == "__main__":
    main()