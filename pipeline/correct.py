import sys
import os

# Add the root project directory to the Python path
# This allows us to import from config.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import anthropic
from config import CLAUDE_API_KEY, CLAUDE_MODEL, CLAUDE_MAX_TOKENS


def correct_transcript(raw_text):
    """
    Stage 2 — AI Transcript Correction

    This function takes a raw, imperfect transcript produced by Vosk
    and sends it to Claude AI for correction.

    Claude fixes:
    - Spelling mistakes (e.g. 'shold' → 'should')
    - Missing punctuation (e.g. adds full stops and question marks)
    - Capitalisation (e.g. 'i think' → 'I think')

    Claude does NOT change the meaning of the sentence.
    Claude returns only the corrected sentence — no extra explanation.

    This process is known as Natural Language Processing (NLP),
    specifically text normalisation.

    Time complexity:  O(n) where n is the length of the input text
    Space complexity: O(n) for storing the corrected text

    Args:
        raw_text (str): The raw imperfect transcript from Vosk
        e.g. 'i think we shold fokus on soshal media'

    Returns:
        str: The corrected transcript from Claude
        e.g. 'I think we should focus on social media.'
    """

    # Initialise the Anthropic client with our API key
    client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

    # Send the raw transcript to Claude with clear instructions
    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=CLAUDE_MAX_TOKENS,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Correct the spelling, punctuation and grammar of this transcript. "
                    f"Do not change the meaning. "
                    f"Return only the corrected sentence and nothing else: {raw_text}"
                )
            }
        ]
    )

    # Extract and return the corrected text from Claude's response
    return message.content[0].text.strip()