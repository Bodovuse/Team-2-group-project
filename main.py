"""
out the box
    Record short spoken statements from different team members.
    Transcribe the speech with an audio model, such as Vosk.
    Correct the transcript with AI local Ollama.
    Save the results in a CSV dataset.

development
    Enrich your data with Python.
    Validate the dataset before analysis.
    Produce basic speaking analytics.
"""

from voskLib import voskMain

if __name__ == "__main__":
    (
        voskMain()
    )