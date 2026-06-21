"""Simple Vosk example.

This records from the microphone, transcribes speech with Vosk, prints the
transcript, and saves it to transcript.txt.
"""

import json
import queue
from datetime import datetime
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import pandas as pd
import csv


MODEL_PATH = "vosk-model-en-us-0.22-lgraph"
SAMPLE_RATE = 16000
OUTPUT_FILE = "data/transcript.csv"
CSV_COLUMNS = [
    "timestamp",        
    "raw_sentence",    
    "corrected_sentence",             
    "time_taken_sec",     
    "accuracy_score"    
]

q = queue.Queue()

def callback(indata, frames, time, status):
    if status:
        print(status)
    q.put(bytes(indata))

model = Model(MODEL_PATH)
recognizer = KaldiRecognizer(model, SAMPLE_RATE)

def voskMain():

    print("Start speaking. Press Ctrl+C to stop.")

    full_text = ""

    try:
        with sd.RawInputStream(
            samplerate=SAMPLE_RATE,
            blocksize=8000,
            dtype="int16",
            channels=1,
            callback=callback,
        ):
            while True:
                data = q.get()

                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    text = result.get("text", "")
                    if text:
                        print("You said:", text)
                        full_text += text + " "

    except KeyboardInterrupt:
        print("\nStopped recording.")

    # Very important: get the final remaining text.
    final_result = json.loads(recognizer.FinalResult())
    final_text = final_result.get("text", "")

    if final_text:
        print("Final:", final_text)
        full_text += final_text + " "

    timestamp = datetime.now().isoformat()

    with open(OUTPUT_FILE, "r") as inFile:
        rows = inFile.readlines()

    with open(OUTPUT_FILE, "a", newline = "\n", encoding="utf-8") as dataFrame:

        

        writer = csv.writer(dataFrame)
        writer.writerow([timestamp, full_text.strip()])
        # dataFrame.write(f"\n{timestamp}\r")
        # dataFrame.write(full_text.strip())
        # dataFrame.writelines(rows)
        
    print(f"\nSaved to {OUTPUT_FILE}")
    print("Transcript:", full_text.strip())
