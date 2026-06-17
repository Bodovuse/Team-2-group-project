import csv
import os
import sys
from datetime import datetime

# Adds root directory to path so config.py can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import LIVE_RECORDINGS_PATH


def get_all_sessions():
    """
    Scans the live recordings folder and returns a list of all session files.
    Each entry includes the filename, full path, row count and creation date.
    Sorted by creation date with the most recent session first.

    Returns:
        list of dicts — each dict contains:
            filename  — just the filename e.g. meeting-bda-20260614-0930.csv
            path      — full file path
            rows      — number of data rows in the CSV
            date      — formatted creation date string

    Time complexity:  O(n log n) where n is the number of session files
    Space complexity: O(n) for storing session metadata in memory
    """
    if not os.path.exists(LIVE_RECORDINGS_PATH):
        return []

    sessions = []

    for filename in os.listdir(LIVE_RECORDINGS_PATH):
        if filename.endswith(".csv") and filename.startswith("meeting-"):
            path = os.path.join(LIVE_RECORDINGS_PATH, filename)

            try:
                with open(path, newline="", encoding="utf-8") as f:
                    rows = sum(1 for row in csv.DictReader(f))
            except Exception:
                rows = 0

            created = os.path.getmtime(path)
            date_str = datetime.fromtimestamp(created).strftime("%Y-%m-%d %H:%M")

            sessions.append({
                "filename": filename,
                "path": path,
                "rows": rows,
                "date": date_str
            })

    sessions.sort(key=lambda x: x["date"], reverse=True)
    return sessions


def display_sessions(sessions):
    """
    Prints all available sessions in a clean numbered table.
    Shows the session number, filename, row count and recording date.
    Called before every management action so the user always sees
    the current state of their recordings.

    Args:
        sessions (list): list of session dicts from get_all_sessions()

    Time complexity:  O(n) where n is the number of sessions
    Space complexity: O(1)
    """
    print("\n" + "=" * 65)
    print("  AVAILABLE SESSIONS")
    print("=" * 65)

    if not sessions:
        print("\n  No sessions found.")
        return

    print(f"\n  {'#':<5} {'File':<42} {'Rows':<8} {'Date'}")
    print(f"  {'─'*5} {'─'*42} {'─'*8} {'─'*16}")

    for i, session in enumerate(sessions, 1):
        name = session["filename"]
        if len(name) > 40:
            name = name[:37] + "..."
        print(f"  [{i}]  {name:<42} {session['rows']:<8} {session['date']}")


def view_session_summary(sessions):
    """
    Shows a detailed summary of a chosen session.
    Displays speaker breakdown, total rows, model used and recording date.
    The user can type m at any point to return to the main menu.

    Args:
        sessions (list): list of session dicts from get_all_sessions()

    Returns:
        bool: True to stay in manage menu, False to return to main menu

    Time complexity:  O(n) where n is the number of rows in the chosen session
    Space complexity: O(k) where k is the number of unique speakers
    """
    display_sessions(sessions)

    if not sessions:
        return True

    choice = input("\nWhich session to view? (number or m for main menu): ").strip().lower()

    if choice == "m":
        return False

    try:
        index = int(choice) - 1
        if index < 0 or index >= len(sessions):
            print("Invalid selection.")
            return True
    except ValueError:
        print("Please enter a valid number.")
        return True

    session = sessions[index]

    speaker_turns = {}
    model_used = "unknown"

    try:
        with open(session["path"], newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row.get("name", "Unknown")
                speaker_turns[name] = speaker_turns.get(name, 0) + 1
                model_used = row.get("model_used", "unknown")
    except Exception:
        print("Error reading session file.")
        return True

    print("\n" + "=" * 65)
    print(f"  SESSION SUMMARY")
    print("=" * 65)
    print(f"\n  File:         {session['filename']}")
    print(f"  Recorded:     {session['date']}")
    print(f"  Model used:   {model_used}")
    print(f"  Total rows:   {session['rows']}")
    print(f"\n  Speaker breakdown:")
    for speaker, turns in sorted(speaker_turns.items()):
        print(f"    {speaker:<20} {turns} turns")

    back = input("\n  Press Enter to go back or m for main menu: ").strip().lower()
    if back == "m":
        return False
    return True


def delete_sessions(sessions):
    """
    Deletes one or more session files chosen by the user.
    The user can enter a single number, a comma separated list,
    or all to delete everything.
    Type m at any point to cancel and return to the main menu.

    A confirmation step shows exactly what will be deleted before
    anything is removed — preventing accidental data loss.
    After deletion the remaining sessions are displayed automatically.

    Args:
        sessions (list): list of session dicts from get_all_sessions()

    Returns:
        bool: True to stay in manage menu, False to return to main menu

    Time complexity:  O(k) where k is the number of sessions selected
    Space complexity: O(k) for storing selected session indices
    """
    display_sessions(sessions)

    if not sessions:
        return True

    print("\nSelect sessions to delete.")
    print("Examples: 1  or  1,2,3  or  all  or  m for main menu")
    choice = input("\nEnter selection: ").strip().lower()

    if choice == "m":
        return False

    to_delete = []

    if choice == "all":
        to_delete = sessions
    else:
        try:
            indices = [int(x.strip()) - 1 for x in choice.split(",")]
            for i in indices:
                if 0 <= i < len(sessions):
                    to_delete.append(sessions[i])
                else:
                    print(f"  Skipping invalid selection: {i + 1}")
        except ValueError:
            print("Invalid input — please enter numbers separated by commas.")
            return True

    if not to_delete:
        print("No valid sessions selected.")
        return True

    print("\nYou are about to delete:")
    for session in to_delete:
        print(f"  - {session['filename']} ({session['rows']} rows)")

    confirm = input("\nAre you sure? (y / n / m for main menu): ").strip().lower()

    if confirm == "m":
        return False

    if confirm != "y":
        print("Deletion cancelled.")
        return True

    deleted = 0
    for session in to_delete:
        try:
            os.remove(session["path"])
            print(f"  Deleted: {session['filename']}")
            deleted += 1
        except Exception as e:
            print(f"  Error deleting {session['filename']}: {e}")

    print(f"\n{deleted} session(s) deleted successfully.")

    remaining = get_all_sessions()
    if remaining:
        print("\nRemaining sessions:")
        display_sessions(remaining)
    else:
        print("\nNo sessions remaining.")

    return True


def rename_session(sessions):
    """
    Renames a chosen session file.
    The timestamp is preserved from the original filename.
    Type m at any point to cancel and return to the main menu.

    Args:
        sessions (list): list of session dicts from get_all_sessions()

    Returns:
        bool: True to stay in manage menu, False to return to main menu

    Time complexity:  O(1)
    Space complexity: O(1)
    """
    display_sessions(sessions)

    if not sessions:
        return True

    choice = input("\nWhich session to rename? (number or m for main menu): ").strip().lower()

    if choice == "m":
        return False

    try:
        index = int(choice) - 1
        if index < 0 or index >= len(sessions):
            print("Invalid selection.")
            return True
    except ValueError:
        print("Please enter a valid number.")
        return True

    session = sessions[index]

    new_name = input("Enter new name (or m for main menu): ").strip().lower()

    if new_name == "m":
        return False

    new_name = new_name.replace(" ", "-")

    while not new_name:
        print("Name cannot be empty.")
        new_name = input("Enter new name: ").strip().lower().replace(" ", "-")

    parts = session["filename"].replace(".csv", "").split("-")
    timestamp = f"{parts[-2]}-{parts[-1]}"
    new_filename = f"meeting-{new_name}-{timestamp}.csv"
    new_path = os.path.join(LIVE_RECORDINGS_PATH, new_filename)

    try:
        os.rename(session["path"], new_path)
        print(f"\nRenamed to: {new_filename}")
    except Exception as e:
        print(f"Error renaming file: {e}")

    return True


def manage_recordings():
    """
    Main recording management menu.
    Allows the user to view, delete and rename session files.
    Type m at any prompt to return to the main menu immediately.
    Type b at the main manage menu to go back to the main menu.

    Time complexity:  O(n) where n is the number of sessions
    Space complexity: O(n) for storing session metadata
    """
    while True:
        sessions = get_all_sessions()

        print("\n" + "=" * 55)
        print("  MANAGE RECORDINGS")
        print("=" * 55)

        display_sessions(sessions)

        print("\nWhat would you like to do?\n")
        print("  V — View session summary")
        print("  D — Delete session(s)")
        print("  R — Rename a session")
        print("  B — Back to main menu")
        print("  M — Main menu")
        print()

        choice = input("Enter choice: ").strip().upper()

        if choice == "V":
            stay = view_session_summary(sessions)
            if not stay:
                break
        elif choice == "D":
            stay = delete_sessions(sessions)
            if not stay:
                break
        elif choice == "R":
            stay = rename_session(sessions)
            if not stay:
                break
        elif choice in ("B", "M"):
            break
        else:
            print("Please enter V, D, R, B or M.")