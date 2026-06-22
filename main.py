"""
DONE
Record short spoken statements from different team members.
Transcribe the speech with an audio model, such as Vosk.
TODO
Correct the transcript with AI local Ollama.
Save the results in a CSV dataset.
Enrich your data with Python.
Validate the dataset before analysis.
Produce basic speaking analytics.
"""

from libraries.voskLib import voskMain
from libraries.ollamaLib import ollamaMain

if __name__ == "__main__":
    (
        voskMain(),
        ollamaMain()
    )
    