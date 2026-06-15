import csv
import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CSV_FILE_PATH, CSV_COLUMNS, MIN_ROWS_REQUIRED


def validate_csv():
    """
    Stage 4 — Validate the dataset

    Checks the CSV file is complete and correct before analytics runs.
    Prints clear error messages for any issues found.

    Checks performed:
        - CSV file exists
        - CSV has minimum required rows
        - No missing values in required columns
        - timestamp is a valid datetime
        - time_taken_sec is numeric and greater than 0
        - num_words is numeric and greater than 0
        - speech_rate_wps is numeric and greater than 0
        - question_flag is a boolean value
        - speaker_turn_id is numeric and greater than 0
        - model_used is one of model1, model2 or model3
        - sentiment is one of positive, negative or neutral

    Time complexity:  O(n) where n is the number of rows
    Space complexity: O(n) to store all rows in memory
    """

    errors = []

    # Check file exists
    if not os.path.exists(CSV_FILE_PATH):
        print(f"Validation failed: CSV file not found at '{CSV_FILE_PATH}'")
        return False

    rows = []
    with open(CSV_FILE_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    # Check minimum rows
    if len(rows) < MIN_ROWS_REQUIRED:
        errors.append(
            f"CSV has {len(rows)} rows — minimum required is {MIN_ROWS_REQUIRED}"
        )

    valid_models = {"model1", "model2", "model3"}
    valid_sentiments = {"positive", "negative", "neutral"}
    valid_flags = {"True", "False"}

    for i, row in enumerate(rows, start=2):

        row_label = f"Row {i}"

        # Check no missing values
        for col in CSV_COLUMNS:
            if not row.get(col, "").strip():
                errors.append(f"{row_label}: missing value in column '{col}'")

        # Check timestamp is valid
        try:
            datetime.fromisoformat(row["timestamp"])
        except ValueError:
            errors.append(
                f"{row_label}: timestamp '{row['timestamp']}' is not a valid datetime"
            )

        # Check time_taken_sec is numeric and greater than 0
        try:
            if float(row["time_taken_sec"]) <= 0:
                errors.append(
                    f"{row_label}: time_taken_sec must be greater than 0"
                )
        except ValueError:
            errors.append(
                f"{row_label}: time_taken_sec '{row['time_taken_sec']}' is not numeric"
            )

        # Check num_words is numeric and greater than 0
        try:
            if int(row["num_words"]) <= 0:
                errors.append(
                    f"{row_label}: num_words must be greater than 0"
                )
        except ValueError:
            errors.append(
                f"{row_label}: num_words '{row['num_words']}' is not numeric"
            )

        # Check speech_rate_wps is numeric and greater than 0
        try:
            if float(row["speech_rate_wps"]) <= 0:
                errors.append(
                    f"{row_label}: speech_rate_wps must be greater than 0"
                )
        except ValueError:
            errors.append(
                f"{row_label}: speech_rate_wps '{row['speech_rate_wps']}' is not numeric"
            )

        # Check question_flag is boolean
        if row["question_flag"] not in valid_flags:
            errors.append(
                f"{row_label}: question_flag '{row['question_flag']}' must be True or False"
            )

        # Check speaker_turn_id is numeric and greater than 0
        try:
            if int(row["speaker_turn_id"]) <= 0:
                errors.append(
                    f"{row_label}: speaker_turn_id must be greater than 0"
                )
        except ValueError:
            errors.append(
                f"{row_label}: speaker_turn_id '{row['speaker_turn_id']}' is not numeric"
            )

        # Check model_used is valid
        if row["model_used"] not in valid_models:
            errors.append(
                f"{row_label}: model_used '{row['model_used']}' must be model1, model2 or model3"
            )

        # Check sentiment is valid
        if row["sentiment"] not in valid_sentiments:
            errors.append(
                f"{row_label}: sentiment '{row['sentiment']}' must be positive, negative or neutral"
            )

    # Print results
    if errors:
        print(f"\nValidation failed — {len(errors)} issue(s) found:\n")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print(f"\nValidation passed — {len(rows)} rows checked, no issues found.")
        return True


if __name__ == "__main__":
    validate_csv()