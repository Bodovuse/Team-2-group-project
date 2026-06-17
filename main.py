import warnings
import os
import sys

# Suppress all warnings — keeps the terminal clean for the user
warnings.filterwarnings("ignore")

# Suppress Vosk LOG messages — set before any imports so it applies globally
os.environ["VOSK_LOG_LEVEL"] = "-1"

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

    m returns to the main menu.
    q quits the program entirely.

    Returns:
        tuple: (model_choice, adapter, model_used)
               model_choice — int 1, 2 or 3, or None if user pressed m
               adapter      — the loaded adapter module for the chosen model
               model_used   — string label for the CSV column

    Time complexity:  O(1)
    Space complexity: O(1)
    """
    print("\nWhich model would you like to use?\n")
    print("  1 — Vosk lgraph + Ollama    (fast, offline, less accurate)")
    print("  2 — Vosk full + Claude      (accurate, requires internet)")
    print("  3 — Faster-Whisper + Claude (most accurate, requires internet)")
    print("  m — Back to main menu")
    print("  q — Quit")
    print()

    while True:
        choice = input("Enter choice (1, 2, 3, m or q): ").strip().lower()
        if choice == "1":
            from models.model1 import adapter
            return 1, adapter, "model1"
        elif choice == "2":
            from models.model2 import adapter
            return 2, adapter, "model2"
        elif choice == "3":
            from models.model3 import adapter
            return 3, adapter, "model3"
        elif choice == "m":
            return None, None, None
        elif choice == "q":
            print("\nGoodbye!")
            sys.exit(0)
        print("Please enter 1, 2, 3, m or q.")


def select_analytics_dataset():
    """
    Asks the user which dataset to run analytics on.
    Shows both synthetic datasets and live recording sessions.
    Returns the file path of the chosen dataset or None if user pressed m.

    m returns to the main menu.
    q quits the program entirely.

    Returns:
        str or None: full file path of the chosen CSV dataset

    Time complexity:  O(n) where n is the number of live sessions
    Space complexity: O(n) for storing session list
    """
    from config import CSV_FILE_PATH
    from pipeline.manage import get_all_sessions

    print("\nWhich dataset would you like to run analytics on?\n")
    print("  1 — Synthetic formal meeting (meetings1-formal.csv)")

    sessions = get_all_sessions()
    for i, session in enumerate(sessions, 2):
        print(f"  {i} — {session['filename']} ({session['rows']} rows, {session['date']})")

    print("  m — Back to main menu")
    print("  q — Quit")
    print()

    options = {"1": CSV_FILE_PATH}
    for i, session in enumerate(sessions, 2):
        options[str(i)] = session["path"]

    while True:
        choice = input(f"Enter choice (1-{len(options)}, m or q): ").strip().lower()
        if choice == "q":
            print("\nGoodbye!")
            sys.exit(0)
        elif choice == "m":
            return None
        if choice in options:
            return options[choice]
        print(f"Please enter a number between 1 and {len(options)}, m or q.")


def main():
    """
    Central controller for the Meeting Speech Analytics Pipeline.

    This is the entry point for the entire project.
    It presents the main menu and routes the user to the correct feature.

    Universal navigation rules applied throughout the entire program:
        m — return to this main menu from anywhere
        q — quit the program entirely from anywhere

    Menu options:
        1 — Start a new recording session
        2 — Manage existing recordings
        3 — Run analytics on a dataset
        4 — Exit
        q — Quit

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
        print("  q — Quit")
        print()

        choice = input("Enter choice: ").strip().lower()

        if choice == "1":
            model_choice, adapter, model_used = select_model()
            if model_choice is None:
                continue
            from pipeline.session import run_session
            run_session(model_choice, adapter, model_used)

        elif choice == "2":
            from pipeline.manage import manage_recordings
            manage_recordings()

        elif choice == "3":
            csv_path = select_analytics_dataset()
            if csv_path is None:
                continue

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

        elif choice in ("4", "q"):
            print("\nGoodbye!")
            break

        elif choice == "m":
            continue

        else:
            print("Please enter 1, 2, 3, 4 or q.")


if __name__ == "__main__":
    main()