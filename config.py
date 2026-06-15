import os
from dotenv import load_dotenv

# Loads API key from .env file
# Keeps sensitive credentials out of the codebase
load_dotenv()


# ─────────────────────────────────────────
# Claude API
# Used for LLM-based transcript correction in model2 and model3
# Corrects spelling, punctuation and grammar without changing meaning
# This is known as text normalisation in NLP
# ─────────────────────────────────────────
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
CLAUDE_MODEL = "claude-sonnet-4-6"
CLAUDE_MAX_TOKENS = 1024


# ─────────────────────────────────────────
# Model 1 — Vosk lgraph + Ollama
# Lightweight ASR model (128MB) paired with a local LLM
# Fully offline — no internet required
# Faster but less accurate than the full Vosk model
# ─────────────────────────────────────────
MODEL1_VOSK_PATH = "asr/vosk-model-en-us-0.22-lgraph"
MODEL1_OLLAMA_MODEL = "gemma3"
MODEL1_OLLAMA_URL = "http://localhost:11434"


# ─────────────────────────────────────────
# Model 2 — Vosk full + Claude
# Full accuracy ASR model (1.8GB) paired with a cloud LLM
# Higher transcription accuracy than lgraph
# Requires internet connection for Claude API
# ─────────────────────────────────────────
MODEL2_VOSK_PATH = "asr/vosk-model-en-us-0.22"


# ─────────────────────────────────────────
# Model 3 — Faster-Whisper + Claude
# Reimplementation of OpenAI Whisper using CTranslate2
# Up to 4x faster than standard Whisper with same accuracy
# Processes complete audio files rather than live streaming
# Device set to CPU for cross-platform compatibility
# ─────────────────────────────────────────
MODEL3_WHISPER_SIZE = "large-v3"
MODEL3_WHISPER_DEVICE = "cpu"
MODEL3_WHISPER_COMPUTE = "int8"


# ─────────────────────────────────────────
# Audio recording settings
# Used by model1 and model2 for live microphone input
# Vosk requires 16000 Hz sample rate and mono audio
# ─────────────────────────────────────────
SAMPLE_RATE = 16000
CHUNK_SIZE = 4096
CHANNELS = 1


# ─────────────────────────────────────────
# Dataset settings
# Central CSV file shared across all pipeline stages
# 10 columns required by assignment + 3 additional improvements
# ─────────────────────────────────────────
CSV_FILE_PATH = "datasets/meetings.csv"
CSV_COLUMNS = [
    "timestamp",        # date and time of recording
    "name",             # speaker name
    "raw_text_vosk",    # raw ASR output before correction
    "text",             # LLM corrected transcript
    "time_taken_sec",   # duration of spoken sentence
    "question_flag",    # True if sentence ends with ?
    "num_words",        # word count of corrected text
    "text_size_chars",  # character count of corrected text
    "speech_rate_wps",  # words per second
    "speaker_turn_id",  # nth time this speaker has spoken
    "sentiment",        # positive, negative or neutral
    "model_used",       # which model recorded this row
    "accuracy_score"    # similarity between raw and corrected text
]


# ─────────────────────────────────────────
# Reports output paths
# Charts and analytics saved here after pipeline runs
# ─────────────────────────────────────────
REPORTS_PATH = "reports"
CHARTS_PATH = "reports/charts"


# ─────────────────────────────────────────
# Validation
# Minimum rows required by the assignment brief
# ─────────────────────────────────────────
MIN_ROWS_REQUIRED = 25