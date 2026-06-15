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
# We chose claude-sonnet-4-6 for its accuracy on short correction tasks
# ─────────────────────────────────────────
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
CLAUDE_MODEL = "claude-sonnet-4-6"
CLAUDE_MAX_TOKENS = 1024


# ─────────────────────────────────────────
# Model 1 — Vosk lgraph + Ollama
# The lightweight version of Vosk at 128MB — fast but less accurate
# Uses a reduced language graph which speeds things up at the cost of accuracy
# Ollama runs the gemma3 LLM locally so no internet is needed at all
# Good for offline use but produces the most transcription errors of the three
# ─────────────────────────────────────────
MODEL1_VOSK_PATH = "asr/vosk-model-en-us-0.22-lgraph"
MODEL1_OLLAMA_MODEL = "gemma3"
MODEL1_OLLAMA_URL = "http://localhost:11434"


# ─────────────────────────────────────────
# Model 2 — Vosk full + Claude
# The full 1.8GB Vosk model — significantly more accurate than lgraph
# Uses advanced neural network algorithms for better transcription quality
# Claude API handles the correction so an internet connection is required
# Best balance between accuracy and familiarity with the Vosk ecosystem
# ─────────────────────────────────────────
MODEL2_VOSK_PATH = "asr/vosk-model-en-us-0.22"


# ─────────────────────────────────────────
# Model 3 — Faster-Whisper + Claude
# Faster-Whisper is a reimplementation of OpenAI Whisper using CTranslate2
# Up to 4x faster than standard Whisper with the same level of accuracy
# Uses the large-v3 model which is the most accurate English model available
# Unlike Vosk it processes complete audio files rather than live streaming
# Set to run on CPU so it works on any machine without a GPU
# ─────────────────────────────────────────
MODEL3_WHISPER_SIZE = "large-v3"
MODEL3_WHISPER_DEVICE = "cpu"
MODEL3_WHISPER_COMPUTE = "int8"


# ─────────────────────────────────────────
# Audio recording settings
# Used by model1 and model2 for live microphone input
# Vosk specifically requires 16000 Hz and mono audio to work correctly
# CHUNK_SIZE controls how often audio chunks are sent to Vosk for processing
# ─────────────────────────────────────────
SAMPLE_RATE = 16000
CHUNK_SIZE = 4096
CHANNELS = 1


# ─────────────────────────────────────────
# Synthetic dataset settings
# Used for testing and showcasing the pipeline without real recordings
# Three scenarios to show how models handle different speaking styles
# meetings1-formal.csv    — formal project meeting
# meetings2-informal.csv  — casual team catch up
# meetings3-conference.csv — academic conference style
# ─────────────────────────────────────────
CSV_FILE_PATH = "datasets/meetings1-formal.csv"


# ─────────────────────────────────────────
# Live recording datasets
# Separate CSV files for real recordings from each model
# These get wiped at the start of each new recording session
# and appended to during the session
# ─────────────────────────────────────────
LIVE_CSV_MODEL1 = "datasets/live/live-model1.csv"
LIVE_CSV_MODEL2 = "datasets/live/live-model2.csv"
LIVE_CSV_MODEL3 = "datasets/live/live-model3.csv"


# ─────────────────────────────────────────
# CSV column structure
# 10 columns required by the assignment + 3 additional improvements
# All pipeline stages read and write using these column names
# ─────────────────────────────────────────
CSV_COLUMNS = [
    "timestamp",        # date and time of recording
    "name",             # speaker name
    "raw_text_vosk",    # raw ASR output before correction
    "text",             # LLM corrected transcript
    "time_taken_sec",   # duration of spoken sentence in seconds
    "question_flag",    # True if the sentence ends with a question mark
    "num_words",        # word count of the corrected text
    "text_size_chars",  # character count of the corrected text
    "speech_rate_wps",  # words per second — num_words divided by time
    "speaker_turn_id",  # how many times this speaker has spoken so far
    "sentiment",        # positive, negative or neutral via TextBlob
    "model_used",       # which model produced this row — model1, 2 or 3
    "accuracy_score"    # how similar the raw text is to the corrected text
]


# ─────────────────────────────────────────
# Reports and charts output
# Analytics results and charts are saved here after the pipeline runs
# Both folders are excluded from GitHub via .gitignore
# ─────────────────────────────────────────
REPORTS_PATH = "reports"
CHARTS_PATH = "reports/charts"


# ─────────────────────────────────────────
# Validation threshold
# The assignment requires a minimum of 25 rows in the final dataset
# The validation stage checks this before running analytics
# ─────────────────────────────────────────
MIN_ROWS_REQUIRED = 25