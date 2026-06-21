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
from langchain_ollama import OllamaLLM
from langchain_experimental.agents.agent_toolkits import create_csv_agent

#CHANGE TO PASSING OLLAMA A FILE AND A PROMPT
MODEL_NAME = "gemma3"
OLLAMA_URL = "http://localhost:11434/api/generate"
DATA = "data/transcript.csv"

def ollamaMain():
    llm = OllamaLLM(model = MODEL_NAME, temperature=0.5)
    agent = create_csv_agent(llm, DATA, verbose = True, allow_dangerous_code = True)
    agent.handle_parsing_errors = True
    agent.invoke("Correct this transcript. correct the raw sentence and put them in the column called corrected sentence")

# def askOllama(prompt):
#     response = requests.post(
#         OLLAMA_URL,
#         json={"model": MODEL_NAME, "prompt": prompt,  "stream": False},
#         timeout=120,
#     )
#     response.raise_for_status()
#     return response.json()["response"].strip()

# def ollamaMain():

#     #rows = []

#     # with open('data/transcript.csv', 'rt') as f:
#     #     reader = csv.reader(f)
#     #     for row in reader:
#     #         rows.append(row)

#     #data = "data/transcript.txt"
#     #data = askOllama(rows)
#     prompt = (
#         "Correct this transcript. correct the raw text and add to a column called corrected text:\n"
#         "$DATA'data/transcript.csv'"
#     ) 
#     output = askOllama(prompt)
#     print("Ollama query sucsessful: ", output)


    