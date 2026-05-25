"""Simple Vosk example.

This records from the microphone, transcribes speech with Vosk, prints the
transcript, and saves it to transcript.txt.
"""

import json
import queue
from datetime import datetime
import sounddevice as sd
from vosk import Model, KaldiRecognizer


MODEL_PATH = "vosk-model-en-us-0.22-lgraph"
SAMPLE_RATE = 16000
OUTPUT_FILE = "transcript.txt"

q = queue.Queue()


def callback(indata, frames, time, status):
    if status:
        print(status)
    q.put(bytes(indata))


model = Model(MODEL_PATH)
recognizer = KaldiRecognizer(model, SAMPLE_RATE)

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

with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
    f.write(f"\n--- {timestamp} ---\n")
    f.write(full_text.strip() + "\n")

print(f"\nSaved to {OUTPUT_FILE}")
print("Transcript:", full_text.strip())
