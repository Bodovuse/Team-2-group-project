import json
import queue
import os
import sys
from vosk import Model, KaldiRecognizer
import sounddevice as sd

# Adds root directory to path so config.py can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import MODEL2_VOSK_PATH, SAMPLE_RATE, CHUNK_SIZE


# Audio queue — acts as a buffer between the microphone and Vosk
# sounddevice continuously pushes audio chunks in
# Vosk pulls them out one at a time and processes them
# Without this buffer the microphone and Vosk would be out of sync
audio_queue = queue.Queue()


def callback(indata, frames, time, status):
    """
    Triggered automatically by sounddevice for every chunk of audio captured.
    Acts as the bridge between the microphone and Vosk —
    pushes raw audio bytes into the queue for Vosk to process.

    This function runs in a separate thread managed by sounddevice.
    It should be as fast as possible — just push to queue and return.
    Any heavy processing here would cause audio dropouts.
    """
    if status:
        print(f"Audio warning: {status}")
    audio_queue.put(bytes(indata))


def load():
    """
    Loads the full 1.8GB Vosk model from the asr/ folder.

    The full model (vosk-model-en-us-0.22) uses a complete language graph
    which makes it significantly more accurate than the lgraph variant.
    The trade off is it takes longer to load and uses more memory.
    It only loads once per session so the delay only happens at the start.

    Exits cleanly with a helpful error message if the model folder is missing
    rather than crashing with a cryptic Python error.

    Returns:
        KaldiRecognizer: loaded Vosk recogniser ready for transcription

    Time complexity:  O(1) — model loads once regardless of input size
    Space complexity: O(n) where n is the model size loaded into memory
    """
    if not os.path.exists(MODEL2_VOSK_PATH):
        print(f"Error: Vosk model not found at '{MODEL2_VOSK_PATH}'")
        print("Download from: https://alphacephei.com/vosk/models")
        sys.exit(1)

    print("Loading Vosk full model — this may take a moment...")
    model = Model(MODEL2_VOSK_PATH)

    # KaldiRecognizer is Vosk's speech recognition engine
    # It processes audio chunks at the specified sample rate
    # and detects when a complete sentence has been spoken
    recognizer = KaldiRecognizer(model, SAMPLE_RATE)
    print("Model loaded successfully.")
    return recognizer


def transcribe(recognizer):
    """
    Listens to the microphone in real time and transcribes speech using Vosk.

    Audio is streamed in small chunks via sounddevice — each chunk is pushed
    into the audio queue by the callback function and pulled out here by Vosk.
    Vosk processes each chunk and detects when a complete sentence has been spoken.
    As soon as a sentence is detected the raw transcript is returned immediately.

    This function only handles transcription — it does not correct the text.
    Correction is handled separately by pipeline/correct.py after this returns.
    This separation is what allows session.py to work with any model uniformly.

    This is a blocking function — it keeps the microphone open and listening
    until Vosk detects a complete sentence, then returns and closes the stream.
    session.py calls this repeatedly in a loop to capture multiple sentences.

    Args:
        recognizer: loaded Vosk KaldiRecognizer instance returned by load()

    Returns:
        tuple: (raw_text, time_taken)
               raw_text   — the raw imperfect transcript from Vosk
               time_taken — how long the sentence took in seconds
               returns (None, None) if interrupted before any speech detected

    Time complexity:  O(n) where n is the number of audio chunks processed
    Space complexity: O(k) where k is CHUNK_SIZE in bytes
    """
    from datetime import datetime

    # Start timing as soon as the microphone opens
    start_time = datetime.now()

    try:
        with sd.RawInputStream(
            samplerate=SAMPLE_RATE,
            blocksize=CHUNK_SIZE,
            dtype="int16",
            channels=1,
            callback=callback,
        ):
            while True:
                # Pull the next audio chunk from the queue
                data = audio_queue.get()

                # AcceptWaveform returns True when Vosk detects a complete sentence
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    raw_text = result.get("text", "").strip()

                    if raw_text:
                        # Calculate how long the sentence took
                        time_taken = (datetime.now() - start_time).total_seconds()
                        return raw_text, time_taken

    except KeyboardInterrupt:
        # Catch any final words Vosk hadn't finished processing when interrupted
        final = json.loads(recognizer.FinalResult()).get("text", "").strip()
        if final:
            time_taken = (datetime.now() - start_time).total_seconds()
            return final, time_taken
        return None, None