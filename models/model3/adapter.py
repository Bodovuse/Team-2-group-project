import wave
import tempfile
import os
import sys
import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

# Adds root directory to path so config.py can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import (
    MODEL3_WHISPER_SIZE,
    MODEL3_WHISPER_DEVICE,
    MODEL3_WHISPER_COMPUTE,
    SAMPLE_RATE,
)


def load():
    """
    Loads the Faster-Whisper large-v3 model and returns it ready for transcription.

    Faster-Whisper is a reimplementation of OpenAI's Whisper model built on
    CTranslate2 — a highly optimised inference engine for transformer models.
    This makes it up to 4x faster than the original Whisper implementation
    while producing identical transcription accuracy.

    The large-v3 model is the most accurate English model in the Whisper family.
    It handles accents, background noise and natural conversational speech
    significantly better than the smaller variants like base or medium.

    On first run the model downloads automatically from HuggingFace and caches
    locally — subsequent runs load from cache without re-downloading.

    Set to run on CPU with int8 quantisation for cross-platform compatibility.
    No GPU required — works on Mac, Windows and Linux out of the box.

    The key difference from Vosk is that Whisper cannot stream in real time.
    It must receive a complete audio file and process it as a whole.
    Session.py controls when recording starts and stops — the adapter
    just records a chunk and transcribes it when told to.

    Returns:
        WhisperModel: loaded Faster-Whisper model ready for transcription

    Time complexity:  O(1) after initial download — loads once per session
    Space complexity: O(n) where n is the model size loaded into memory
    """
    print("Loading Faster-Whisper large-v3 model — this may take a moment...")
    print("On first run the model will download automatically from HuggingFace.")

    model = WhisperModel(
        MODEL3_WHISPER_SIZE,
        device=MODEL3_WHISPER_DEVICE,
        compute_type=MODEL3_WHISPER_COMPUTE
    )

    print("Model loaded successfully.")
    return model


def record_chunk(duration):
    """
    Records audio from the microphone for a fixed duration.
    Returns the raw audio as a numpy array ready for transcription.
    No threading — simple blocking record then return.

    Args:
        duration (int): how many seconds to record

    Returns:
        numpy array of float32 audio samples

    Time complexity:  O(n) where n is the duration in seconds
    Space complexity: O(n) for storing the audio samples in memory
    """
    audio = sd.rec(
        int(duration * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32"
    )
    sd.wait()
    return audio.flatten()


def transcribe(model, audio):
    """
    Transcribes a numpy audio array using Faster-Whisper.

    Takes pre-recorded audio and passes it to Whisper for transcription.
    The audio is saved to a temporary wav file because Whisper requires
    a file path rather than raw audio data in memory.
    The temporary file is deleted immediately after transcription.

    This function is intentionally simple — it just transcribes what it receives.
    All recording control logic lives in session.py which decides when to
    record and when to stop. This keeps the adapter focused on one thing only.

    Args:
        model: loaded WhisperModel instance returned by load()
        audio: numpy float32 array of recorded audio samples

    Returns:
        str: raw transcript from Faster-Whisper
             returns None if nothing was detected

    Time complexity:  O(n log n) for Whisper inference where n is audio duration
    Space complexity: O(n) for the temporary wav file
    """
    # Save to a temporary wav file — Whisper requires a file path not raw data
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp_path = tmp.name

    with wave.open(tmp_path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        # Convert float32 to int16 — wav format requires int16
        audio_int16 = (audio * 32767).astype(np.int16)
        wf.writeframes(audio_int16.tobytes())

    # Transcribe — language="en" forces English for better accuracy
    segments, _ = model.transcribe(tmp_path, language="en")
    raw_text = " ".join(segment.text.strip() for segment in segments).strip()

    # Delete the temporary file immediately
    os.unlink(tmp_path)

    return raw_text if raw_text else None
