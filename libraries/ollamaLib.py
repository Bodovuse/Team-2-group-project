"""Simple Ollama example.

Enter a prompt, send it to a local Ollama model, and print the output.

Before running:
    1. Install Ollama from https://ollama.com/download
    2. Open the Ollama app, or make sure the local Ollama server is running
       at http://localhost:11434
    3. Open new terminal
    4. Download the model:
       ollama pull gemma3
"""
# input CSV file
# output to CSV file
import csv
import requests


MODEL_NAME = "gemma3"
OLLAMA_URL = "http://localhost:11434/api/generate"
DATA = "data/transcript.csv"

def askOllama(prompt):
    response = requests.post(
        OLLAMA_URL,
        json={"model": MODEL_NAME, "prompt": prompt,  "stream": False},
        timeout=360,
    )
    response.raise_for_status()
    return response.json()["response"].strip()

def ollamaMain():

    rows = []

    print("Ollama initiated\n")

    with open("data/transcript.csv", "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            raw_sentence = row["raw_sentence"]
            prompt = (f"Correct grammar and wording in the raw text column and return only corrected text: {raw_sentence}")
            output = askOllama(prompt)
            print(output)

            row["corrected_sentence"] = output
            rows.append(row)

    with open("data/transcript.csv", "w", newline="", encoding="utf-8") as f:
        fieldnames = rows[0].keys()

        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print("Ollama done\n")
    


    