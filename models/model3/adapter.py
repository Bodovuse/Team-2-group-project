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
    WHISPER_TURN_DURATION
)


def load():
    """
    Loads the Faster-Whisper large-v3 model and returns it ready for transcription.

    Faster-Whisper is a reimplementation of OpenAI's Whisper model built on
    CTranslate2 — a highly optimised inference engine for transformer models.
    This makes it up to 4x faster than the original Whisper implementation
    while producing identical transcription accuracy.

    The large-v3 model is chosen because it is the most accurate English model
    in the Whisper family. It handles accents, background noise and natural
    conversational speech better than the smaller variants.

    On first run the model downloads automatically from HuggingFace and caches
    to the local machine. Subsequent runs load from cache and are much faster.
    The cache location is managed by HuggingFace Hub automatically.

    Set to run on CPU with int8 quantisation for cross-platform compatibility.
    int8 reduces memory usage while keeping accuracy close to float32.
    No GPU is required — works on Mac, Windows and Linux out of the box.

    The fundamental difference between this and the Vosk adapter is that
    Whisper cannot stream audio in real time. It must receive a complete
    audio file and process it as a whole. This means transcribe() records
    a fixed duration first then processes — unlike Vosk which transcribes
    as the user speaks.

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


def transcribe(model):
    """
    Records audio from the microphone for a fixed duration then transcribes
    it using the Faster-Whisper large-v3 model.

    Because Whisper processes complete audio files rather than streaming,
    this function works in two distinct phases:

        Phase 1 — Record:
            Opens the microphone and records for WHISPER_TURN_DURATION seconds.
            The duration is configured in config.py and defaults to 10 seconds.
            sounddevice captures the audio as a numpy float32 array.
            sd.wait() blocks the thread until recording is complete.

        Phase 2 — Transcribe:
            The numpy array is converted to int16 and saved to a temporary wav file.
            Whisper requires a file path rather than raw audio data in memory.
            The wav file is passed to Whisper which processes it as a whole.
            All detected speech segments are joined into one complete transcript.
            The temporary wav file is deleted immediately after transcription
            to avoid leaving audio files on disk.

    This function only handles transcription — it does not correct the output.
    Correction is handled separately by pipeline/correct.py after this returns.
    This separation keeps the adapter focused on one responsibility and allows
    session.py to call any model's transcribe() function in the same way.

    The trade off vs model2 is that the speaker must speak within the fixed
    recording window. If they speak for longer than WHISPER_TURN_DURATION
    seconds the recording cuts off. The duration can be adjusted in config.py.

    Args:
        model: loaded WhisperModel instance returned by load()

    Returns:
        tuple: (raw_text, time_taken)
               raw_text   — raw transcript string from Faster-Whisper
               time_taken — total recording duration in seconds
               returns (None, None) if no speech was detected in the recording

    Time complexity:  O(n log n) for Whisper inference where n is audio duration
    Space complexity: O(n) for storing audio samples in memory before transcription
    """
    from datetime import datetime

    print(f"  Recording for {WHISPER_TURN_DURATION} seconds — speak now!")

    start_time = datetime.now()

    # Record audio from the microphone for the configured duration
    # sd.rec() is non-blocking — sd.wait() blocks until recording finishes
    audio = sd.rec(
        int(WHISPER_TURN_DURATION * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32"
    )
    sd.wait()

    time_taken = (datetime.now() - start_time).total_seconds()
    print("  Recording complete — transcribing...")

    # Flatten from 2D array (samples x channels) to 1D for processing
    audio = audio.flatten()

    # Save audio to a temporary wav file because Whisper requires
    # a file path as input rather than raw audio data in memory
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp_path = tmp.name

    with wave.open(tmp_path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        # Convert float32 samples to int16 — wav format requires int16
        # Multiply by 32767 to scale from -1.0/1.0 range to int16 range
        audio_int16 = (audio * 32767).astype(np.int16)
        wf.writeframes(audio_int16.tobytes())

    # Transcribe the wav file — language="en" forces English detection
    # which improves accuracy for English speech over auto-detection
    segments, _ = model.transcribe(tmp_path, language="en")

    # Whisper returns multiple segments — join them into one complete transcript
    raw_text = " ".join(segment.text.strip() for segment in segments).strip()

    # Delete the temporary wav file immediately — no audio stored on disk
    os.unlink(tmp_path)

    if raw_text:
        return raw_text, time_taken
    else:
        # Nothing detected — session.py will handle prompting the user to try again
        print("  Nothing detected — please try again.")
        return None, None