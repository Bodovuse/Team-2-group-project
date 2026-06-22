import csv
import os
import sys
from collections import defaultdict
import matplotlib.pyplot as plt

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CSV_FILE_PATH, REPORTS_PATH, CHARTS_PATH


def load_csv():
    """
    Loads the CSV dataset into memory.
    Returns a list of row dictionaries.

    Time complexity:  O(n) where n is the number of rows
    Space complexity: O(n) to store all rows in memory
    """
    rows = []
    with open(CSV_FILE_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def get_model2_rows(rows):
    """
    Filters rows to only model2 to avoid triple counting.
    Since all three models record the same sentence,
    we use model2 as the reference for speaker statistics.

    Time complexity:  O(n)
    Space complexity: O(n)
    """
    return [row for row in rows if row["model_used"] == "model2"]


def analyse_speakers(rows):
    """
    Calculates per speaker statistics.
    Uses model2 rows only to avoid counting each sentence three times.

    Returns a dictionary of speaker stats.

    Time complexity:  O(n)
    Space complexity: O(k) where k is the number of unique speakers
    """
    stats = defaultdict(lambda: {
        "total_words": 0,
        "total_time": 0.0,
        "questions": 0,
        "turns": 0,
        "total_speech_rate": 0.0
    })

    for row in rows:
        name = row["name"]
        stats[name]["total_words"] += int(row["num_words"])
        stats[name]["total_time"] += float(row["time_taken_sec"])
        stats[name]["turns"] += 1
        stats[name]["total_speech_rate"] += float(row["speech_rate_wps"])
        if row["question_flag"] == "True":
            stats[name]["questions"] += 1

    # Calculate averages
    for name in stats:
        turns = stats[name]["turns"]
        stats[name]["avg_time"] = round(
            stats[name]["total_time"] / turns, 2
        ) if turns > 0 else 0
        stats[name]["avg_speech_rate"] = round(
            stats[name]["total_speech_rate"] / turns, 2
        ) if turns > 0 else 0

    return stats


def analyse_models(rows):
    """
    Calculates average accuracy score per model.
    Shows which model produced the most accurate transcriptions.

    Time complexity:  O(n)
    Space complexity: O(k) where k is the number of models
    """
    model_scores = defaultdict(list)

    for row in rows:
        model_scores[row["model_used"]].append(float(row["accuracy_score"]))

    model_averages = {}
    for model in model_scores:
        scores = model_scores[model]
        model_averages[model] = round(sum(scores) / len(scores), 3)

    return model_averages


def analyse_sentiment(rows):
    """
    Calculates sentiment distribution per speaker.
    Uses model2 rows only to avoid triple counting.

    Time complexity:  O(n)
    Space complexity: O(k) where k is the number of unique speakers
    """
    sentiment_stats = defaultdict(lambda: {
        "positive": 0, "negative": 0, "neutral": 0
    })

    for row in rows:
        name = row["name"]
        sentiment = row["sentiment"]
        if sentiment in sentiment_stats[name]:
            sentiment_stats[name][sentiment] += 1

    return sentiment_stats


def save_charts(speaker_stats, model_averages, sentiment_stats):
    """
    Generates and saves bar charts to the reports/charts folder.

    Charts produced:
        1. Total words per speaker
        2. Total speaking time per speaker
        3. Questions asked per speaker
        4. Average speech rate per speaker
        5. Model accuracy comparison
        6. Sentiment distribution per speaker

    Time complexity:  O(k) where k is the number of unique speakers
    Space complexity: O(1) per chart
    """
    os.makedirs(CHARTS_PATH, exist_ok=True)

    speakers = list(speaker_stats.keys())
    colors = ["#4C9BE8", "#E8834C", "#4CE87A"]

    # Chart 1 — Total words per speaker
    plt.figure(figsize=(8, 5))
    plt.bar(speakers, [speaker_stats[s]["total_words"] for s in speakers], color=colors)
    plt.title("Total words per speaker")
    plt.xlabel("Speaker")
    plt.ylabel("Total words")
    plt.tight_layout()
    plt.savefig(f"{CHARTS_PATH}/total_words.png")
    plt.close()

    # Chart 2 — Total speaking time per speaker
    plt.figure(figsize=(8, 5))
    plt.bar(speakers, [speaker_stats[s]["total_time"] for s in speakers], color=colors)
    plt.title("Total speaking time per speaker (seconds)")
    plt.xlabel("Speaker")
    plt.ylabel("Seconds")
    plt.tight_layout()
    plt.savefig(f"{CHARTS_PATH}/speaking_time.png")
    plt.close()

    # Chart 3 — Questions asked per speaker
    plt.figure(figsize=(8, 5))
    plt.bar(speakers, [speaker_stats[s]["questions"] for s in speakers], color=colors)
    plt.title("Questions asked per speaker")
    plt.xlabel("Speaker")
    plt.ylabel("Questions")
    plt.tight_layout()
    plt.savefig(f"{CHARTS_PATH}/questions.png")
    plt.close()

    # Chart 4 — Average speech rate per speaker
    plt.figure(figsize=(8, 5))
    plt.bar(speakers, [speaker_stats[s]["avg_speech_rate"] for s in speakers], color=colors)
    plt.title("Average speech rate per speaker (words per second)")
    plt.xlabel("Speaker")
    plt.ylabel("Words per second")
    plt.tight_layout()
    plt.savefig(f"{CHARTS_PATH}/speech_rate.png")
    plt.close()

    # Chart 5 — Model accuracy comparison
    models = list(model_averages.keys())
    plt.figure(figsize=(8, 5))
    plt.bar(models, [model_averages[m] for m in models], color=colors)
    plt.title("Average accuracy score per model")
    plt.xlabel("Model")
    plt.ylabel("Accuracy score (0-1)")
    plt.ylim(0, 1)
    plt.tight_layout()
    plt.savefig(f"{CHARTS_PATH}/model_accuracy.png")
    plt.close()

    # Chart 6 — Sentiment distribution per speaker
    x = range(len(speakers))
    width = 0.25
    pos_vals = [sentiment_stats[s]["positive"] for s in speakers]
    neg_vals = [sentiment_stats[s]["negative"] for s in speakers]
    neu_vals = [sentiment_stats[s]["neutral"] for s in speakers]

    plt.figure(figsize=(9, 5))
    plt.bar([i - width for i in x], pos_vals, width, label="Positive", color="#4CE87A")
    plt.bar(x, neu_vals, width, label="Neutral", color="#4C9BE8")
    plt.bar([i + width for i in x], neg_vals, width, label="Negative", color="#E8834C")
    plt.title("Sentiment distribution per speaker")
    plt.xlabel("Speaker")
    plt.ylabel("Number of sentences")
    plt.xticks(x, speakers)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{CHARTS_PATH}/sentiment.png")
    plt.close()

    print(f"Charts saved to {CHARTS_PATH}/")


def print_analytics(speaker_stats, model_averages, sentiment_stats):
    """
    Prints a formatted analytics report to the terminal.

    Time complexity:  O(k) where k is the number of unique speakers
    Space complexity: O(1)
    """
    print("\n" + "=" * 55)
    print("  MEETING SPEECH ANALYTICS REPORT")
    print("=" * 55)

    # Sort speakers by total words
    sorted_by_words = sorted(
        speaker_stats.items(), key=lambda x: x[1]["total_words"], reverse=True
    )

    print("\n--- Speaking statistics ---\n")
    print(f"  {'Speaker':<12} {'Words':>8} {'Time(s)':>10} {'Avg Rate':>12} {'Questions':>12}")
    print(f"  {'-'*12} {'-'*8} {'-'*10} {'-'*12} {'-'*12}")
    for name, stats in sorted_by_words:
        print(
            f"  {name:<12} {stats['total_words']:>8} "
            f"{stats['total_time']:>10.1f} "
            f"{stats['avg_speech_rate']:>12.2f} "
            f"{stats['questions']:>12}"
        )

    print("\n--- Key findings ---\n")
    most_words = sorted_by_words[0]
    least_words = sorted_by_words[-1]
    total_time = sum(s["total_time"] for s in speaker_stats.values())
    avg_time = total_time / len(speaker_stats)
    most_questions = max(speaker_stats.items(), key=lambda x: x[1]["questions"])

    print(f"  Most words:              {most_words[0]} ({most_words[1]['total_words']} words)")
    print(f"  Least words:             {least_words[0]} ({least_words[1]['total_words']} words)")
    print(f"  Total speaking time:     {total_time:.1f} seconds")
    print(f"  Avg time per speaker:    {avg_time:.1f} seconds")
    print(f"  Most questions asked:    {most_questions[0]} ({most_questions[1]['questions']} questions)")

    print("\n--- Top 5 speakers by speaking time ---\n")
    sorted_by_time = sorted(
        speaker_stats.items(), key=lambda x: x[1]["total_time"], reverse=True
    )[:5]
    for i, (name, stats) in enumerate(sorted_by_time, 1):
        print(f"  {i}. {name} — {stats['total_time']:.1f} seconds")

    print("\n--- Model accuracy comparison ---\n")
    for model, avg in sorted(model_averages.items(), key=lambda x: x[1], reverse=True):
        bar = "█" * int(avg * 20)
        print(f"  {model:<10} {avg:.3f}  {bar}")

    print("\n--- Sentiment per speaker ---\n")
    for name in speaker_stats:
        s = sentiment_stats[name]
        print(f"  {name:<12} positive: {s['positive']:>3}  neutral: {s['neutral']:>3}  negative: {s['negative']:>3}")

    print("\n" + "=" * 55)


def run_analytics():
    """
    Main analytics function.
    Loads the CSV, runs all analyses, prints results and saves charts.
    """
    if not os.path.exists(CSV_FILE_PATH):
        print(f"Error: CSV file not found at '{CSV_FILE_PATH}'")
        return

    print("Loading dataset...")
    rows = load_csv()
    model2_rows = get_model2_rows(rows)

    print(f"Analysing {len(rows)} rows ({len(model2_rows)} unique sentences)...")

    speaker_stats = analyse_speakers(model2_rows)
    model_averages = analyse_models(rows)
    sentiment_stats = analyse_sentiment(model2_rows)

    print_analytics(speaker_stats, model_averages, sentiment_stats)
    save_charts(speaker_stats, model_averages, sentiment_stats)


if __name__ == "__main__":
    run_analytics()