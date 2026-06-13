import os
from dotenv import load_dotenv

# Loads API key from .env file
# Keeps sensitive credentials out of the codebase
load_dotenv()


# Claude API configuration
# Used in Stage 2 to correct raw Vosk transcripts
# claude-sonnet-4-6 selected for accuracy and speed
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
CLAUDE_MODEL = "claude-sonnet-4-6"
CLAUDE_MAX_TOKENS = 1024


# Vosk speech recognition model path
# Full 1.8GB model selected for higher transcription accuracy
# Download from: https://alphacephei.com/vosk/models
VOSK_MODEL_PATH = "model/vosk-model-en-us-0.22"


# CSV file path and required column structure
# All pipeline stages read and write to this file
CSV_FILE_PATH = "data/meetings.csv"
CSV_COLUMNS = [
    "timestamp",        # date and time of recording
    "name",             # speaker name
    "raw_text_vosk",    # raw transcript from Vosk
    "text",             # corrected transcript from Claude
    "time_taken_sec",   # duration of spoken sentence in seconds
    "question_flag",    # True if sentence ends with ?
    "num_words",        # word count of corrected text
    "text_size_chars",  # character count of corrected text
    "speech_rate_wps",  # words per second
    "speaker_turn_id"   # sequential turn number per speaker
]


# PyAudio microphone settings
# Vosk requires 16000 Hz sample rate and mono input
SAMPLE_RATE = 16000
CHUNK_SIZE = 4096
CHANNELS = 1


# Minimum dataset size required for submission
MIN_ROWS_REQUIRED = 25