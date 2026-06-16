import anthropic
import os
import sys

# Adds root directory to path so config.py can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CLAUDE_API_KEY, CLAUDE_MODEL, CLAUDE_MAX_TOKENS


def correct_transcript(raw_text):
    """
    Sends a raw ASR transcript to Claude for correction.
    Used by both model2 (Vosk full) and model3 (Faster-Whisper) —
    keeping correction logic in one place rather than duplicating it.

    Claude fixes spelling, punctuation and grammar without changing the meaning.
    This is the text normalisation step in the NLP pipeline.

    Whisper tends to produce fewer errors than Vosk so fewer corrections
    are expected for model3 — but Claude still fixes any remaining issues.

    The prompt is strict — Claude returns only the corrected sentence
    with no notes, explanations or commentary added.

    Args:
        raw_text (str): raw imperfect transcript from any ASR model
        e.g. 'i think we shold fokus on soshal media'

    Returns:
        str: corrected transcript from Claude
        e.g. 'I think we should focus on social media.'

    Time complexity:  O(n) where n is the length of the input text
    Space complexity: O(n) for storing the corrected output
    """
    client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=CLAUDE_MAX_TOKENS,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Correct the spelling, punctuation and grammar of this transcript. "
                    f"Do not change the meaning. "
                    f"Do not add any notes, explanations or commentary. "
                    f"Return only the corrected sentence with absolutely no extra text: {raw_text}"
                )
            }
        ]
    )

    return message.content[0].text.strip()