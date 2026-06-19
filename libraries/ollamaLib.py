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
#import ollama

#CHANGE TO PASSING OLLAMA A FILE AND A PROMPT
MODEL_NAME = "gemma3"
OLLAMA_URL = "http://localhost:11434/api/generate"

def askOllama(prompt):
    response = requests.post(
        OLLAMA_URL,
        json={"model": MODEL_NAME, "prompt": prompt, "stream": False},
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["response"].strip()

def ollamaMain():

    rows = []

    # with open('data/transcript.csv', 'rt') as f:
    #     reader = csv.reader(f)
    #     for row in reader:
    #         rows.append(row)

    data = "data/transcript.txt"
    #data = askOllama(rows)
    prompt = f'take this input {data}, and correct the raw input and return only corrected text' 
    output = askOllama(prompt)
    print("Ollama query sucsessful: ", output)
    